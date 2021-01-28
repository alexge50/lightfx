import ast
import asyncio
import contextlib
import io
import pickle
import struct
import sys
import traceback


async def receive(reader):
    size = struct.unpack('>I', await reader.readexactly(4))[0]
    payload = await reader.readexactly(size)
    data = pickle.loads(payload)

    return data


def send(writer, data):
    serialized_data = pickle.dumps(data)
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

            if type(data) != str:
                send(writer, {'error': 'unsupported input format'})

            input_ast = ast.parse(data)
            is_expression = False
            expression_value = None

            async with context.state() as state:
                try:

                    with string_stdout() as stdout:
                        if len(input_ast.body) == 1 and isinstance(input_ast.body[0], ast.Expr):
                            expression_value = eval(data)
                            is_expression = True
                        else:
                            exec(data)
                except Exception:
                    message = traceback.format_exc()
                    send(writer, {'traceback': message})
                finally:
                    if is_expression:
                        send(writer, {'success': {'value': str(expression_value), 'stdout': stdout.getvalue()}})
                    else:
                        send(writer, {'success': {'stdout': stdout.getvalue()}})

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
