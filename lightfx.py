import asyncio
import argparse
import struct
import pickle


async def receive(reader):
    size = struct.unpack('>I', await reader.readexactly(4))[0]
    payload = await reader.readexactly(size)
    data = pickle.loads(payload)

    return data


def send(writer, data):
    serialized_data = pickle.dumps(data)
    writer.write(struct.pack('>I', len(serialized_data)))
    writer.write(serialized_data)


async def main(command=None):
    reader, writer = await asyncio.open_unix_connection('/tmp/lightfx.sock')

    try:
        if command is None:
            user_input = input('>>> ')
            while user_input.strip() != 'q':
                send(writer, user_input)
                print(await receive(reader))
                user_input = input('>>> ')

        else:
            send(writer, command)
            print(await receive(reader))

        writer.close()
    except asyncio.IncompleteReadError:
        print('Server disconnected')


parser = argparse.ArgumentParser(description='lightfx cli tool.')
parser.add_argument('command', type=str, help='command can be shell, effect or options')
parser.add_argument('argument', type=str, nargs='?', default=None, help='argument for effect or options command')
parser.add_argument('--list', action='store_true', help='list effects/options description')

args = parser.parse_args()

if args.command == 'shell':
    asyncio.run(main())
elif args.command == 'effect':
    if args.argument is None:
        if args.list:
            asyncio.run(main('state.effects'))
        else:
            asyncio.run(main('state.current_effect'))
    else:
        asyncio.run(main(f"state.current_effect = '{args.argument}'"))
elif args.command == 'options':
    if args.argument is None:
        asyncio.run(main('state.options'))
    else:
        asyncio.run(main(f"state.options = {args.argument}"))
else:
    print(f'command {args.command} not recognized')
