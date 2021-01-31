import asyncio
import argparse
import struct

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
        while user_input.strip() != 'q':
            send(writer, {
                'action': 'exec',
                'value': user_input
            })
            print(await receive(reader))
            user_input = input('>>> ')

        writer.close()
    except asyncio.IncompleteReadError:
        print('Server disconnected')


async def get(field):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')
    send(writer, {
        'action': 'get',
    })

    result = await receive(reader)

    print(result['success'][field])

    writer.close()


async def set_effect(effect):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')
    send(writer, {
        'action': 'get',
    })

    result = (await receive(reader))['success']
    result['effect'] = effect

    send(writer, {
        'action': 'set',
        'value': result
    })

    writer.close()


parser = argparse.ArgumentParser(description='lightfx cli tool.')
parser.add_argument('command', type=str, help='command can be shell, effect or options')
parser.add_argument('argument', type=str, nargs='?', default=None, help='argument for effect or options command')
parser.add_argument('--list', action='store_true', help='list effects/options description')

args = parser.parse_args()

if args.command == 'shell':
    asyncio.run(exec())
elif args.command == 'effect':
    if args.argument is None:
        if args.list:
            asyncio.run(get('effects'))
        else:
            asyncio.run(get('effect'))
    else:
        asyncio.run(set_effect(args.argument))
elif args.command == 'options':
    if args.argument is None:
        asyncio.run(get('options'))
    else:
        print('unimplemented')
else:
    print(f'command {args.command} not recognized')
