import asyncio
import apigpio

BT1_GPIO = 18
BT2_GPIO = 23


def on_input(gpio, level, tick):
    print('on_input {} {} {}'.format(gpio, level, tick))


async def subscribe(pi):

    await pi.set_mode(BT1_GPIO, apigpio.INPUT)
    await pi.set_mode(BT2_GPIO, apigpio.INPUT)

    await pi.add_callback(BT1_GPIO, edge=apigpio.RISING_EDGE,
                               func=on_input)
    await pi.add_callback(BT2_GPIO, edge=apigpio.RISING_EDGE,
                               func=on_input)


async def main():
    address = ('192.168.1.3', 8888)
    pi = apigpio.Pi()
    await pi.connect(address)
    await subscribe(pi)
    asyncio.get_event_loop.run_forever()

if __name__ == '__main__':
    asyncio.run(main())