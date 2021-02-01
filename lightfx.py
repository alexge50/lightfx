import ast
import asyncio
import argparse
import struct
import sys
import readline

import jsonplus


async def receive(reader):
    size = struct.unpack('>I', await reader.readexactly(4))[0]
    payload = await reader.readexactly(size)
    data = jsonplus.loads(payload.decode())

    return data


def send(writer, data):
    serialized_data = jsonplus.dumps(data).encode()
    writer.write(struct.pack('>I', len(serialized_data)))
    writer.write(serialized_data)


async def exec():
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')

    try:
        user_input = input('>>> ')
        while True:
            try:
                ast.parse(user_input)
            except SyntaxError:
                more_input = input('... ')
                while more_input != '':
                    user_input += '\n' + more_input
                    more_input = input('... ')

            send(writer, {
                'action': 'exec',
                'value': user_input
            })
            result = await receive(reader)

            if result['state'] == 'failed':
                print(result['traceback'], file=sys.stderr)
            else:
                if 'value' in result:
                    print(result['value'])
                print(result['stdout'])

            user_input = input('>>> ')
    except asyncio.IncompleteReadError:
        print('Server disconnected')
    except EOFError:
        writer.close()


async def get(field):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')
    send(writer, {
        'action': 'get',
    })

    result = await receive(reader)

    if result['state'] == 'success':
        print(result['value'][field])
    else:
        print("getting state failed", file=sys.stderr)

    writer.close()


async def set_effect(effect):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')
    send(writer, {
        'action': 'get',
    })

    result = (await receive(reader))['value']
    result['effect'] = effect

    send(writer, {
        'action': 'set',
        'value': result
    })

    result = await receive(reader)

    if result['state'] == 'success':
        print(f'effect set to {effect}')
    else:
        print(f'Error: {result["value"]}', file=sys.stderr)

    writer.close()


async def set_top_level_options(options):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')
    send(writer, {
        'action': 'get',
    })

    result = (await receive(reader))['value']
    result['options'] = options

    send(writer, {
        'action': 'set',
        'value': result
    })

    result = await receive(reader)

    if result['state'] == 'success':
        print(f'options updated')
    else:
        print(f'Error: {result["value"]}', file=sys.stderr)

    writer.close()


async def set_options_fields(options_fields: [(str, object)]):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')
    send(writer, {
        'action': 'get',
    })

    result = (await receive(reader))['value']

    options_type = type(result['options'])
    options = result['options']._asdict()
    for name, value in options_fields:
        options[name] = value

    result['options'] = options_type(**options)

    send(writer, {
        'action': 'set',
        'value': result
    })

    result = await receive(reader)

    if result['state'] == 'success':
        print(f'options updated')
    else:
        print(f'Error: {result["value"]}', file=sys.stderr)

    writer.close()


parser = argparse.ArgumentParser(description='lightfx cli tool.')
parser.add_argument('command', type=str, help='command can be shell, effect or options')
parser.add_argument('arguments', type=str, nargs='*', default=None, help='argument for effect or options command')
parser.add_argument('--list', action='store_true', help='list effects/options description')

args = parser.parse_args()

if args.command == 'shell':
    asyncio.run(exec())
elif args.command == 'effect':
    if len(args.arguments) == 0:
        if args.list:
            asyncio.run(get('effects'))
        else:
            asyncio.run(get('effect'))
    else:
        asyncio.run(set_effect(args.arguments[0]))
elif args.command == 'options':
    if len(args.arguments) == 0:
        asyncio.run(get('options'))
    else:
        if len(args.arguments) == 1:
            asyncio.run(set_top_level_options(eval(args.arguments[0], {}, {})))
        elif len(args.arguments) % 2 == 0:
            arguments = [(name, eval(value, {}, {})) for name, value in zip(args.arguments[0::2], args.arguments[1::2])]
            asyncio.run(set_options_fields(arguments))
        else:
            print('incorrect number of arguments')
else:
    print(f'command {args.command} not recognized')
