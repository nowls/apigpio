import asyncio
import apigpio

LED_GPIO = 21

async def start(pi, address, gpio):
    await pi.connect(address)

    await pi.set_mode(gpio, apigpio.OUTPUT)

    # Create the script.
    script = 'w {e} 1 mils 500 w {e} 0 mils 500 w {e} 1 mils 500 w {e} 0'\
        .format(e=gpio)
    sc_id = await pi.store_script(script)

    # Run the script.
    await pi.run_script(sc_id)

    await asyncio.sleep(5)

    await pi.delete_script(sc_id)

async def main():
    address = ('192.168.1.3', 8888)
    pi = apigpio.Pi()
    await pi.connect(address)
    await start(pi, address, LED_GPIO)
 
if __name__ == '__main__':
    asyncio.run(main())
