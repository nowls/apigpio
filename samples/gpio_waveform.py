import asyncio
import apigpio


LED_GPIO = 21

async def start(pi, address, gpio, cycles=5, period=1.0, duty=0.5):
    '''
    Blink an LED using the waveform API.

    address:= the (host, port) tuple used to connect to pigpiod
       gpio:= the GPIO to control
     cycles:= the number of cycles to blink the LED
     period:= the period in seconds
       duty:= the duty cycle
    '''
    await pi.connect(address)

    await pi.set_mode(gpio, apigpio.OUTPUT)


    # Create the waveform.
    period_usec = int(period * 1000000)
    hi_usec = int(period_usec * duty)
    lo_usec = period_usec - hi_usec
    waveform = []
    for i in range(cycles):
        waveform.append(apigpio.Pulse(1<<LED_GPIO, 0, hi_usec))
        waveform.append(apigpio.Pulse(0, 1<<LED_GPIO, lo_usec))

    # Run the waveform.
    await pi.wave_clear()
    await pi.wave_add_generic(waveform)

    try:
        wid = await pi.wave_create()
    except apigpio.apigpio.ApigpioError as e:
        print(f"Error creating waveform: {e.value}")
        return

    await pi.wave_send_once(wid)
    while (await pi.wave_tx_busy()):
        await asyncio.sleep(0.1)
    await pi.wave_delete(wid)

async def main():
    address = ('192.168.1.3', 8888)
    pi = apigpio.Pi()
    await pi.connect(address)
    await start(pi, address, LED_GPIO)

if __name__ == '__main__':
    asyncio.run(main())
