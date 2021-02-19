import asyncio
import apigpio

LED_GPIO = 21

async def start_blink(pi, address):
    await pi.connect(address)

    await pi.set_mode(LED_GPIO, apigpio.OUTPUT)

    while True:
        await pi.write(LED_GPIO, 0)
        await asyncio.sleep(1)
        await pi.write(LED_GPIO, 1)
        await asyncio.sleep(1)

async def main():
    address = ('192.168.1.3', 8888)
    pi = apigpio.Pi()
    await pi.connect(address)
    await start_blink(pi, address, LED_GPIO)
 
if __name__ == '__main__':
    asyncio.run(main())
