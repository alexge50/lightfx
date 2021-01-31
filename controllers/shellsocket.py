import ast
import asyncio
import contextlib
import io
import struct
import sys
import traceback

import jsonplus

import core.effects


async def receive(reader):
    size = struct.unpack('>I', await reader.readexactly(4))[0]
    payload = await reader.readexactly(size)
    data = jsonplus.loads(payload.decode())

    return data


def send(writer, data):
    serialized_data = jsonplus.dumps(data).encode()
    writer.write(struct.pack('>I', len(serialized_data)))
    writer.write(serialized_data)


@contextlib.contextmanager
def string_stdout():
    old = sys.stdout
    stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


async def handle_connection(context, reader, writer):
    try:
        while True:
            data = await receive(reader)

            if data['action'] == 'exec':
                exec_string = data['value']

                input_ast = ast.parse(exec_string)
                is_expression = False
                expression_value = None

                async with context.state() as state:
                    try:
                        with string_stdout() as stdout:
                            if len(input_ast.body) == 1 and isinstance(input_ast.body[0], ast.Expr):
                                expression_value = eval(exec_string)
                                is_expression = True
                            else:
                                exec(exec_string)
                    except Exception:
                        message = traceback.format_exc()
                        send(writer, {'traceback': message})
                    finally:
                        if is_expression:
                            send(writer, {'success': {'value': repr(expression_value), 'stdout': stdout.getvalue()}})
                        else:
                            send(writer, {'success': {'stdout': stdout.getvalue()}})
            elif data['action'] == 'get':
                async with context.state() as state:
                    send(writer, {'success': {
                        'delta_time': state.delta_time,
                        'effect': str(state.current_effect),
                        'options': state.options,
                        'effects': state.effects
                    }})
            elif data['action'] == 'set':
                value = data['value']

                if str((await context.read_only_state()).current_effect) != value['effect']:
                    await context.set_effect(value['effect'])

                state = await context.read_only_state()
                if '_asdict' in dir(value['options']) and \
                   '__name__' in value['options'] and \
                   core.effects.is_effect_type(state.current_effect):
                    await context.set_options(type(state.current_effect).options_type()(**value['options']._asdict()))
                else:
                    await context.set_options(value['options'])

    except asyncio.IncompleteReadError:
        pass


class ShellSocket:
    def __init__(self, socket_path):
        self._server = None
        self._socket_path = socket_path
        self._context = None

    async def start(self, context):
        self._context = context

        async def _handle_connection(reader, writer):
            await handle_connection(self._context, reader, writer)

        self._server = await asyncio.start_unix_server(
            _handle_connection,
            self._socket_path,
        )

        await self._server.start_serving()
