import asyncio
import socket
import struct
import sys
import functools
from .ctes import *

exceptions = True

# pigpio command numbers
_PI_CMD_MODES = 0
_PI_CMD_MODEG = 1
_PI_CMD_PUD = 2
_PI_CMD_READ = 3
_PI_CMD_WRITE = 4
_PI_CMD_PWM = 5
_PI_CMD_PRS = 6
_PI_CMD_PFS = 7
_PI_CMD_SERVO = 8
_PI_CMD_WDOG = 9
_PI_CMD_BR1 = 10
_PI_CMD_BR2 = 11
_PI_CMD_BC1 = 12
_PI_CMD_BC2 = 13
_PI_CMD_BS1 = 14
_PI_CMD_BS2 = 15
_PI_CMD_TICK = 16
_PI_CMD_HWVER = 17

_PI_CMD_NO = 18
_PI_CMD_NB = 19
_PI_CMD_NP = 20
_PI_CMD_NC = 21

_PI_CMD_PRG = 22
_PI_CMD_PFG = 23
_PI_CMD_PRRG = 24
_PI_CMD_HELP = 25
_PI_CMD_PIGPV = 26

_PI_CMD_WVCLR = 27
_PI_CMD_WVAG = 28
_PI_CMD_WVAS = 29
_PI_CMD_WVGO = 30
_PI_CMD_WVGOR = 31
_PI_CMD_WVBSY = 32
_PI_CMD_WVHLT = 33
_PI_CMD_WVSM = 34
_PI_CMD_WVSP = 35
_PI_CMD_WVSC = 36

_PI_CMD_TRIG = 37

_PI_CMD_PROC = 38
_PI_CMD_PROCD = 39
_PI_CMD_PROCR = 40
_PI_CMD_PROCS = 41

_PI_CMD_SLRO = 42
_PI_CMD_SLR = 43
_PI_CMD_SLRC = 44

_PI_CMD_PROCP = 45
_PI_CMD_MICRO = 46
_PI_CMD_MILLI = 47
_PI_CMD_PARSE = 48

_PI_CMD_WVCRE = 49
_PI_CMD_WVDEL = 50
_PI_CMD_WVTX = 51
_PI_CMD_WVTXR = 52
_PI_CMD_WVNEW = 53

_PI_CMD_I2CO = 54
_PI_CMD_I2CC = 55
_PI_CMD_I2CRD = 56
_PI_CMD_I2CWD = 57
_PI_CMD_I2CWQ = 58
_PI_CMD_I2CRS = 59
_PI_CMD_I2CWS = 60
_PI_CMD_I2CRB = 61
_PI_CMD_I2CWB = 62
_PI_CMD_I2CRW = 63
_PI_CMD_I2CWW = 64
_PI_CMD_I2CRK = 65
_PI_CMD_I2CWK = 66
_PI_CMD_I2CRI = 67
_PI_CMD_I2CWI = 68
_PI_CMD_I2CPC = 69
_PI_CMD_I2CPK = 70

_PI_CMD_SPIO = 71
_PI_CMD_SPIC = 72
_PI_CMD_SPIR = 73
_PI_CMD_SPIW = 74
_PI_CMD_SPIX = 75

_PI_CMD_SERO = 76
_PI_CMD_SERC = 77
_PI_CMD_SERRB = 78
_PI_CMD_SERWB = 79
_PI_CMD_SERR = 80
_PI_CMD_SERW = 81
_PI_CMD_SERDA = 82

_PI_CMD_GDC = 83
_PI_CMD_GPW = 84

_PI_CMD_HC = 85
_PI_CMD_HP = 86

_PI_CMD_CF1 = 87
_PI_CMD_CF2 = 88

_PI_CMD_FG = 97
_PI_CMD_FN = 98

_PI_CMD_NOIB = 99

_PI_CMD_BI2CC = 89
_PI_CMD_BI2CO = 90
_PI_CMD_BI2CZ = 91

_PI_CMD_I2CZ = 92

_PI_CMD_WVCHA = 93

_PI_CMD_SLRI = 94

# pigpio error text

_errors = {  
   PI_INIT_FAILED: "pigpio initialisation failed",
   PI_BAD_USER_GPIO: "gpio not 0-31",
   PI_BAD_GPIO: "gpio not 0-53",
   PI_BAD_MODE: "mode not 0-7",
   PI_BAD_LEVEL: "level not 0-1",
   PI_BAD_PUD: "pud not 0-2",
   PI_BAD_PULSEWIDTH: "pulsewidth not 0 or 500-2500",
   PI_BAD_DUTYCYCLE: "dutycycle not 0-range (default 255)",
   PI_BAD_TIMER: "timer not 0-9",
   PI_BAD_MS: "ms not 10-60000",
   PI_BAD_TIMETYPE: "timetype not 0-1",
   PI_BAD_SECONDS: "seconds < 0",
   PI_BAD_MICROS: "micros not 0-999999",
   PI_TIMER_FAILED: "gpioSetTimerFunc failed",
   PI_BAD_WDOG_TIMEOUT: "timeout not 0-60000",
   PI_NO_ALERT_FUNC: "DEPRECATED",
   PI_BAD_CLK_PERIPH: "clock peripheral not 0-1",
   PI_BAD_CLK_SOURCE: "DEPRECATED",
   PI_BAD_CLK_MICROS: "clock micros not 1, 2, 4, 5, 8, or 10",
   PI_BAD_BUF_MILLIS: "buf millis not 100-10000",
   PI_BAD_DUTYRANGE: "dutycycle range not 25-40000",
   PI_BAD_SIGNUM: "signum not 0-63",
   PI_BAD_PATHNAME: "can't open pathname",
   PI_NO_HANDLE: "no handle available",
   PI_BAD_HANDLE: "unknown handle",
   PI_BAD_IF_FLAGS: "ifFlags > 3",
   PI_BAD_CHANNEL: "DMA channel not 0-14",
   PI_BAD_SOCKET_PORT: "socket port not 1024-30000",
   PI_BAD_FIFO_COMMAND: "unknown fifo command",
   PI_BAD_SECO_CHANNEL: "DMA secondary channel not 0-6",
   PI_NOT_INITIALISED: "function called before gpioInitialise",
   PI_INITIALISED: "function called after gpioInitialise",
   PI_BAD_WAVE_MODE: "waveform mode not 0-1",
   PI_BAD_CFG_INTERNAL: "bad parameter in gpioCfgInternals call",
   PI_BAD_WAVE_BAUD: "baud rate not 50-250000(RX)/1000000(TX)",
   PI_TOO_MANY_PULSES: "waveform has too many pulses",
   PI_TOO_MANY_CHARS: "waveform has too many chars",
   PI_NOT_SERIAL_GPIO: "no bit bang serial read in progress on gpio",
   PI_NOT_PERMITTED: "no permission to update gpio",
   PI_SOME_PERMITTED: "no permission to update one or more gpios",
   PI_BAD_WVSC_COMMND: "bad WVSC subcommand",
   PI_BAD_WVSM_COMMND: "bad WVSM subcommand",
   PI_BAD_WVSP_COMMND: "bad WVSP subcommand",
   PI_BAD_PULSELEN: "trigger pulse length not 1-100",
   PI_BAD_SCRIPT: "invalid script",
   PI_BAD_SCRIPT_ID: "unknown script id",
   PI_BAD_SER_OFFSET: "add serial data offset > 30 minute",
   PI_GPIO_IN_USE: "gpio already in use",
   PI_BAD_SERIAL_COUNT: "must read at least a byte at a time",
   PI_BAD_PARAM_NUM: "script parameter id not 0-9",
   PI_DUP_TAG: "script has duplicate tag",
   PI_TOO_MANY_TAGS: "script has too many tags",
   PI_BAD_SCRIPT_CMD: "illegal script command",
   PI_BAD_VAR_NUM: "script variable id not 0-149",
   PI_NO_SCRIPT_ROOM: "no more room for scripts",
   PI_NO_MEMORY: "can't allocate temporary memory",
   PI_SOCK_READ_FAILED: "socket read failed",
   PI_SOCK_WRIT_FAILED: "socket write failed",
   PI_TOO_MANY_PARAM: "too many script parameters (> 10)",
   PI_NOT_HALTED: "script already running or failed",
   PI_BAD_TAG: "script has unresolved tag",
   PI_BAD_MICS_DELAY: "bad MICS delay (too large)",
   PI_BAD_MILS_DELAY: "bad MILS delay (too large)",
   PI_BAD_WAVE_ID: "non existent wave id",
   PI_TOO_MANY_CBS: "No more CBs for waveform",
   PI_TOO_MANY_OOL: "No more OOL for waveform",
   PI_EMPTY_WAVEFORM: "attempt to create an empty waveform",
   PI_NO_WAVEFORM_ID: "No more waveform ids",
   PI_I2C_OPEN_FAILED: "can't open I2C device",
   PI_SER_OPEN_FAILED: "can't open serial device",
   PI_SPI_OPEN_FAILED: "can't open SPI device",
   PI_BAD_I2C_BUS: "bad I2C bus",
   PI_BAD_I2C_ADDR: "bad I2C address",
   PI_BAD_SPI_CHANNEL: "bad SPI channel",
   PI_BAD_FLAGS: "bad i2c/spi/ser open flags",
   PI_BAD_SPI_SPEED: "bad SPI speed",
   PI_BAD_SER_DEVICE: "bad serial device name",
   PI_BAD_SER_SPEED: "bad serial baud rate",
   PI_BAD_PARAM: "bad i2c/spi/ser parameter",
   PI_I2C_WRITE_FAILED: "I2C write failed",
   PI_I2C_READ_FAILED: "I2C read failed",
   PI_BAD_SPI_COUNT: "bad SPI count",
   PI_SER_WRITE_FAILED: "ser write failed",
   PI_SER_READ_FAILED: "ser read failed",
   PI_SER_READ_NO_DATA: "ser read no data available",
   PI_UNKNOWN_COMMAND: "unknown command",
   PI_SPI_XFER_FAILED: "SPI xfer/read/write failed",
   PI_BAD_POINTER: "bad (NULL) pointer",
   PI_NO_AUX_SPI: "need a A+/B+/Pi2 for auxiliary SPI",
   PI_NOT_PWM_GPIO: "gpio is not in use for PWM",
   PI_NOT_SERVO_GPIO: "gpio is not in use for servo pulses",
   PI_NOT_HCLK_GPIO: "gpio has no hardware clock",
   PI_NOT_HPWM_GPIO: "gpio has no hardware PWM",
   PI_BAD_HPWM_FREQ: "hardware PWM frequency not 1-125M",
   PI_BAD_HPWM_DUTY: "hardware PWM dutycycle not 0-1M",
   PI_BAD_HCLK_FREQ: "hardware clock frequency not 4689-250M",
   PI_BAD_HCLK_PASS: "need password to use hardware clock 1",
   PI_HPWM_ILLEGAL: "illegal: PWM in use for main clock",
   PI_BAD_DATABITS: "serial data bits not 1-32",
   PI_BAD_STOPBITS: "serial (half) stop bits not 2-8",
   PI_MSG_TOOBIG: "socket/pipe message too big",
   PI_BAD_MALLOC_MODE: "bad memory allocation mode",
   PI_TOO_MANY_SEGS: "too many I2C transaction segments",
   PI_BAD_I2C_SEG: "an I2C transaction segment failed",
   PI_BAD_SMBUS_CMD: "SMBus command not supported",
   PI_NOT_I2C_GPIO: "no bit bang I2C in progress on gpio",
   PI_BAD_I2C_WLEN: "bad I2C write length",
   PI_BAD_I2C_RLEN: "bad I2C read length",
   PI_BAD_I2C_CMD: "bad I2C command",
   PI_BAD_I2C_BAUD: "bad I2C baud rate: not 50-500k",
   PI_CHAIN_LOOP_CNT: "bad chain loop count",
   PI_BAD_CHAIN_LOOP: "empty chain loop",
   PI_CHAIN_COUNTER: "too many chain counters",
   PI_BAD_CHAIN_CMD: "bad chain command",
   PI_BAD_CHAIN_DELAY: "bad chain delay micros",
   PI_CHAIN_NESTING: "chain counters nested too deeply",
   PI_CHAIN_TOO_BIG: "chain is too long",
   PI_DEPRECATED: "deprecated function removed",
   PI_BAD_SER_INVERT: "bit bang serial invert not 0 or 1"
}


class ApigpioError(Exception):
    """pigpio module exception"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Pulse:
   """
   A class to store pulse information.
   """

   def __init__(self, gpio_on, gpio_off, delay):
      """
      Initialises a pulse.

       gpio_on:= the GPIO to switch on at the start of the pulse.
      gpio_off:= the GPIO to switch off at the start of the pulse.
         delay:= the delay in microseconds before the next pulse.

      """
      self.gpio_on = gpio_on
      self.gpio_off = gpio_off
      self.delay = delay

def error_text(errnum):
    """
    Returns a text description of a pigpio error.

    errnum:= <0, the error number

    ...
    print(pigpio.error_text(-5))
    level not 0-1
    ...
    """
    return _errors.get(errnum) or "unknown error ({})".format(errnum)

def u2i(uint32):
    """
    Converts a 32 bit unsigned number to signed.

    uint32:= an unsigned 32 bit number

    ...
    print(u2i(4294967272))
    -24
    print(u2i(37))
    37
    ...
    """
    mask = (2 ** 32) - 1
    if uint32 & (1 << 31):
        v = uint32 | ~mask
    else:
        v = uint32 & mask
    return v


def _u2i(uint32):
    """
    Converts a 32 bit unsigned number to signed.  If the number
    is negative it indicates an error.  On error a pigpio
    exception will be raised if exceptions is True.
    """
    v = u2i(uint32)
    if v < 0:
        if exceptions:
            raise ApigpioError(error_text(v))
    return v


class _callback_ADT:
    """An ADT class to hold callback information."""

    def __init__(self, gpio, edge, func):
        """
        Initialises a callback ADT.

        gpio:= Broadcom gpio number.
        edge:= EITHER_EDGE, RISING_EDGE, or FALLING_EDGE.
        func:= a user function taking three arguments (gpio, level, tick).
        """
        self.gpio = gpio
        self.edge = edge
        self._func = func
        self.bit = 1 << gpio

    @property
    def func(self):
        def _f(*args, **kwargs):
            # protect our-self from faulty callbacks
            try:
                self._func(*args, **kwargs)
            except Exception as e:
                print('Exception raised when running callback {}'.format(e))
        return _f


class _callback_handler(object):
    """
    A class to handle callbacks.
    Each instance of this class open it's own connection to gpiod, which is
    only used to listen for notifications.
    """

    def __init__(self, pi):
        self._loop = pi._loop
        self.pi = pi
        self.handle = None
        self.monitor = 0
        self.callbacks = []
        self.f_stop = asyncio.Future(loop=self._loop)
        self.f_stopped = asyncio.Future(loop=self._loop)

    async def _connect(self, address):
        # FIXME: duplication with pi.connect
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Disable the Nagle algorithm.
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.setblocking(False)

        # TODO: handle connection errors !
        await self._loop.sock_connect(self.s, address)
        self.handle = await self._pigpio_aio_command(_PI_CMD_NOIB, 0, 0)
        asyncio.ensure_future(self._wait_for_notif(), loop=self._loop)

    async def close(self):
        if not self.f_stop.done():
            self.handle = await self._pigpio_aio_command(_PI_CMD_NC,
                                                              self.handle, 0)
            self.f_stop.set_result(True)
            await self.f_stopped

    async def _wait_for_notif(self):
        last_level = 0

        while True:
            MSG_SIZ = 12
            f_recv = asyncio.ensure_future(self._loop.sock_recv(self.s, MSG_SIZ))
            done, pending = await asyncio.\
                wait([f_recv, self.f_stop],
                     return_when=asyncio.FIRST_COMPLETED)
            if self.f_stop in done:
                break
            else:
                buf = f_recv.result()
            # buf = await self._loop.sock_recv(self.s, MSG_SIZ)

            while len(buf) < MSG_SIZ:
                await self._loop.sock_recv(self.s, MSG_SIZ-len(buf))

            seq, flags, tick, level = (struct.unpack('HHII', buf))
            if flags == 0:
                changed = level ^ last_level
                last_level = level
                for cb in self.callbacks:
                    if cb.bit & changed:
                        new_level = 0
                        if cb.bit & level:
                            new_level = 1
                        if cb.edge ^ new_level:
                            cb.func(cb.gpio, new_level, tick)
            else:
                if flags & NTFY_FLAGS_WDOG:
                    print('watchdog signal')
                    gpio = flags & NTFY_FLAGS_GPIO
                    for cb in self.callbacks:
                        if cb.gpio == gpio:
                            cb.func(cb.gpio, TIMEOUT, tick)
                if flags & NTFY_FLAGS_ALIVE:
                    print('keep alive signal')
                # no event for now
                # elif flags & NTFY_FLAGS_EVENT:
                #    event = flags & NTFY_FLAGS_GPIO
                #    for cb in self.events:
                #        if cb.event == event:
                #            cb.func(event, tick)
        self.s.close()
        self.f_stopped.set_result(True)
    
    async def append(self, cb):
        """Adds a callback."""
        self.callbacks.append(cb.callb)
        self.monitor = self.monitor | cb.callb.bit

        await self.pi._pigpio_aio_command(_PI_CMD_NB, self.handle,
                                               self.monitor)
    
    async def remove(self, cb):
        """Removes a callback."""
        if cb in self.callbacks:
            self.callbacks.remove(cb)
            new_monitor = 0
            for c in self.callbacks:
                new_monitor |= c.bit
            if new_monitor != self.monitor:
                self.monitor = new_monitor
                await self.pi._pigpio_aio_command(
                    _PI_CMD_NB, self.handle, self.monitor)

    async def _pigpio_aio_command(self, cmd,  p1, p2,):
        # FIXME: duplication with pi._pigpio_aio_command
        data = struct.pack('IIII', cmd, p1, p2, 0)
        await self._loop.sock_sendall(self.s, data)
        response = await self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res

class Callback:
    """A class to provide gpio level change callbacks."""

    def __init__(self, notify, user_gpio, edge=RISING_EDGE, func=None):
        """
        Initialise a callback and adds it to the notification thread.
        """
        self._notify = notify
        self.count = 0
        if func is None:
            func = self._tally
        self.callb = _callback_ADT(user_gpio, edge, func)
        # FIXME await self._notify.append(self.callb)
    
    async def cancel(self):
        """Cancels a callback by removing it from the notification thread."""
        await self._notify.remove(self.callb)

    def _tally(self, user_gpio, level, tick):
        """Increment the callback called count."""
        self.count += 1

    def tally(self):
        """
        Provides a count of how many times the default tally
        callback has triggered.

        The count will be zero if the user has supplied their own
        callback function.
        """
        return self.count


class Pi(object):
    
    async def _pigpio_aio_command(self, cmd,  p1, p2,):
        """
        Runs a pigpio socket command.

        sl:= command socket and lock.
        cmd:= the command to be executed.
        p1:= command parameter 1 (if applicable).
         p2:=  command parameter 2 (if applicable).
        """
        async with self._lock:
            data = struct.pack('IIII', cmd, p1, p2, 0)
            await self._loop.sock_sendall(self.s, data)
            response = await self._loop.sock_recv(self.s, 16)
            _, res = struct.unpack('12sI', response)
            return res
    
    async def _pigpio_aio_command_ext(self, cmd, p1, p2, p3, extents):
        """
        Runs an extended pigpio socket command.

            sl:= command socket and lock.
           cmd:= the command to be executed.
            p1:= command parameter 1 (if applicable).
            p2:= command parameter 2 (if applicable).
            p3:= total size in bytes of following extents
        extents:= additional data blocks
        """
        async with self._lock:
            return (await self._pigpio_aio_command_ext_unlocked(cmd, p1, p2, p3, extents))

    async def _pigpio_aio_command_ext_unlocked(self, cmd, p1, p2, p3, extents):
        """Run extended pigpio socket command without any lock."""
        ext = bytearray(struct.pack('IIII', cmd, p1, p2, p3))
        for x in extents:
            if isinstance(x, str):
                ext.extend(x.encode('latin-1'))
            else:
                ext.extend(x)
        await self._loop.sock_sendall(self.s, ext)
        response = await self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res
    
    async def connect(self, address):
        """
        Connect to a remote or local gpiod daemon.
        :param address: a pair (address, port), the address must be already
        resolved (for example an ip address)
        :return:
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False)
        # Disable the Nagle algorithm.
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        await self._loop.sock_connect(self.s, address)

        await self._notify._connect(address)
    
    async def stop(self):
        """

        :return:
        """
        print('closing notifier')
        await self._notify.close()
        print('closing socket')
        self.s.close()
    
    async def get_version(self):
        res = await self._pigpio_aio_command(_PI_CMD_PIGPV)
        print('version: {}'.format(res))

    async def get_pigpio_version(self):
        """
        Returns the pigpio software version.

        ...
        v = pi.get_pigpio_version()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PIGPV, 0, 0)
    
    async def store_script(self, script):
        """
        Store a script for later execution.

        script:= the script text as a series of bytes.

        Returns a >=0 script id if OK.

        ...
        sid = pi.store_script(
         b'tag 0 w 22 1 mils 100 w 22 0 mils 100 dcr p0 jp 0')
        ...
        """
        if len(script):
            res = await self._pigpio_aio_command_ext(_PI_CMD_PROC, 0, 0,
                                                          len(script),
                                                          [script])
            return _u2i(res)
        else:
            return 0
    
    async def run_script(self, script_id, params=None):
        """
        Runs a stored script.

        script_id:= id of stored script.
         params:= up to 10 parameters required by the script.

        ...
        s = pi.run_script(sid, [par1, par2])

        s = pi.run_script(sid)

        s = pi.run_script(sid, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ...
        """
        # I p1 script id
        # I p2 0
        # I p3 params * 4 (0-10 params)
        # (optional) extension
        # I[] params
        if params is not None:
            ext = bytearray()
            for p in params:
                ext.extend(struct.pack("I", p))
            nump = len(params)
            extents = [ext]
        else:
            nump = 0
            extents = []
        res = await self._pigpio_aio_command_ext(_PI_CMD_PROCR, script_id,
                                                      0, nump * 4, extents)
        return _u2i(res)
    
    async def script_status(self, script_id):
        """
        Returns the run status of a stored script as well as the
        current values of parameters 0 to 9.

        script_id:= id of stored script.

        The run status may be

        . .
        PI_SCRIPT_INITING
        PI_SCRIPT_HALTED
        PI_SCRIPT_RUNNING
        PI_SCRIPT_WAITING
        PI_SCRIPT_FAILED
        . .

        The return value is a tuple of run status and a list of
        the 10 parameters.  On error the run status will be negative
        and the parameter list will be empty.

        ...
        (s, pars) = pi.script_status(sid)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PROCP, script_id, 0)
        bytes = u2i(res)

        if bytes > 0:

            # Fixme : this sould be the same a _rxbuf
            # data = self._rxbuf(bytes)
            data = await self._loop.sock_recv(self.s, bytes)
            while len(data) < bytes:
                b = await self._loop.sock_recv(self.s, bytes-len(data))
                data.extend(b)

            pars = struct.unpack('11i', data)
            status = pars[0]
            params = pars[1:]
        else:
            status = bytes
            params = ()
        return status, params
    
    async def stop_script(self, script_id):
        """
        Stops a running script.

        script_id:= id of stored script.

        ...
        status = pi.stop_script(sid)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PROCS, script_id, 0)
        return _u2i(res)
    
    async def delete_script(self, script_id):
        """
        Deletes a stored script.

        script_id:= id of stored script.

        ...
        status = pi.delete_script(sid)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PROCD, script_id, 0)
        return _u2i(res)

    async def read_bank_1(self):
        """
        Returns the levels of the bank 1 gpios (gpios 0-31).

        The returned 32 bit integer has a bit set if the corresponding
        gpio is high.  Gpio n has bit value (1<<n).

        ...
        print(bin(pi.read_bank_1()))
        0b10010100000011100100001001111
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_BR1, 0, 0)
        return res

    async def clear_bank_1(self, bits):
        """
        Clears gpios 0-31 if the corresponding bit in bits is set.

        bits:= a 32 bit mask with 1 set if the corresponding gpio is
             to be cleared.

        A returned status of PI_SOME_PERMITTED indicates that the user
        is not allowed to write to one or more of the gpios.

        ...
        pi.clear_bank_1(int("111110010000",2))
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_BC1, bits, 0)
        return _u2i(res)

    async def set_bank_1(self, bits):
        """
        Sets gpios 0-31 if the corresponding bit in bits is set.

        bits:= a 32 bit mask with 1 set if the corresponding gpio is
             to be set.

        A returned status of PI_SOME_PERMITTED indicates that the user
        is not allowed to write to one or more of the gpios.

        ...
        pi.set_bank_1(int("111110010000",2))
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_BS1, bits, 0)
        return _u2i(res)
 
    async def set_mode(self, gpio, mode):
        """
        Sets the gpio mode.

        gpio:= 0-53.
        mode:= INPUT, OUTPUT, ALT0, ALT1, ALT2, ALT3, ALT4, ALT5.

        ...
        pi.set_mode( 4, apigpio.INPUT)  # gpio  4 as input
        pi.set_mode(17, apigpio.OUTPUT) # gpio 17 as output
        pi.set_mode(24, apigpio.ALT2)   # gpio 24 as ALT2
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_MODES, gpio, mode)
        return _u2i(res)
    
    async def set_pull_up_down(self, gpio, pud):
        """
        Sets or clears the internal GPIO pull-up/down resistor.
        gpio:= 0-53.
         pud:= PUD_UP, PUD_DOWN, PUD_OFF.
        ...
        await pi.set_pull_up_down(17, apigpio.PUD_OFF)
        await pi.set_pull_up_down(23, apigpio.PUD_UP)
        await pi.set_pull_up_down(24, apigpio.PUD_DOWN)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PUD, gpio, pud)
        return _u2i(res)

    async def get_mode(self, gpio):
        """
        Returns the gpio mode.

        gpio:= 0-53.

        Returns a value as follows

        . .
        0 = INPUT
        1 = OUTPUT
        2 = ALT5
        3 = ALT4
        4 = ALT0
        5 = ALT1
        6 = ALT2
        7 = ALT3
        . .

        ...
        print(pi.get_mode(0))
        4
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_MODEG, gpio, 0)
        return _u2i(res)

    async def write(self, gpio, level):
        """
        Sets the gpio level.

        gpio:= 0-53.
        level:= 0, 1.

        If PWM or servo pulses are active on the gpio they are
        switched off.

        ...
        pi.set_mode(17, pigpio.OUTPUT)

        pi.write(17,0)
        print(pi.read(17))
        0

        pi.write(17,1)
        print(pi.read(17))
        1
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WRITE, gpio, level)
        return _u2i(res)
    
    async def read(self, gpio):
        """
        Returns the GPIO level.
        gpio:= 0-53.
        ...
        await pi.set_mode(23, pigpio.INPUT)
        await pi.set_pull_up_down(23, pigpio.PUD_DOWN)
        print(await pi.read(23))
        0
        await pi.set_pull_up_down(23, pigpio.PUD_UP)
        print(await pi.read(23))
        1
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_READ, gpio, 0)
        return _u2i(res)
    
    async def gpio_trigger(self, user_gpio, pulse_len=10, level=1):
        """
        Send a trigger pulse to a GPIO.  The GPIO is set to
        level for pulse_len microseconds and then reset to not level.
        user_gpio:= 0-31
        pulse_len:= 1-100
            level:= 0-1
        ...
        pi.gpio_trigger(23, 10, 1)
        ...
        """
        # pigpio message format

        # I p1 user_gpio
        # I p2 pulse_len
        # I p3 4
        ## extension ##
        # I level
        extents = [struct.pack("I", level)]
        res = await self._pigpio_aio_command_ext(_PI_CMD_TRIG, user_gpio,
                                                      pulse_len, 4, extents)
        return _u2i(res)
  
    async def set_glitch_filter(self, user_gpio, steady):
        """
        Sets a glitch filter on a GPIO.
        Level changes on the GPIO are not reported unless the level
        has been stable for at least [*steady*] microseconds.  The
        level is then reported.  Level changes of less than [*steady*]
        microseconds are ignored.
        user_gpio:= 0-31
           steady:= 0-300000
        Returns 0 if OK, otherwise PI_BAD_USER_GPIO, or PI_BAD_FILTER.
        This filter affects the GPIO samples returned to callbacks set up
        with [*callback*] and [*wait_for_edge*].
        It does not affect levels read by [*read*],
        [*read_bank_1*], or [*read_bank_2*].
        Each (stable) edge will be timestamped [*steady*]
        microseconds after it was first detected.
        ...
        pi.set_glitch_filter(23, 100)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_FG, user_gpio, steady)
        return _u2i(res)
  
    async def set_noise_filter(self, user_gpio, steady, active):
        """
        Sets a noise filter on a GPIO.
        Level changes on the GPIO are ignored until a level which has
        been stable for [*steady*] microseconds is detected.  Level
        changes on the GPIO are then reported for [*active*]
        microseconds after which the process repeats.
        user_gpio:= 0-31
           steady:= 0-300000
           active:= 0-1000000
        Returns 0 if OK, otherwise PI_BAD_USER_GPIO, or PI_BAD_FILTER.
        This filter affects the GPIO samples returned to callbacks set up
        with [*callback*] and [*wait_for_edge*].
        It does not affect levels read by [*read*],
        [*read_bank_1*], or [*read_bank_2*].
        Level changes before and after the active period may
        be reported.  Your software must be designed to cope with
        such reports.
        ...
        pi.set_noise_filter(23, 1000, 5000)
        ...
        """
        # pigpio message format

        # I p1 user_gpio
        # I p2 steady
        # I p3 4
        ## extension ##
        # I active
        extents = [struct.pack("I", active)]
        res = await self._pigpio_aio_command_ext(_PI_CMD_FN, user_gpio,
                                                      steady, 4, extents)
        return _u2i(res)
 
    async def set_PWM_dutycycle(self, user_gpio, dutycycle):
        """
        Starts (non-zero dutycycle) or stops (0) PWM pulses on the GPIO.
        user_gpio:= 0-31.
        dutycycle:= 0-range (range defaults to 255).
        The [*set_PWM_range*] function can change the default range of 255.
        ...
        pi.set_PWM_dutycycle(4,   0) # PWM off
        pi.set_PWM_dutycycle(4,  64) # PWM 1/4 on
        pi.set_PWM_dutycycle(4, 128) # PWM 1/2 on
        pi.set_PWM_dutycycle(4, 192) # PWM 3/4 on
        pi.set_PWM_dutycycle(4, 255) # PWM full on
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PWM, user_gpio, int(dutycycle))
        return _u2i(res)
    
    async def get_PWM_dutycycle(self, user_gpio):
        """
        Returns the PWM dutycycle being used on the GPIO.
        user_gpio:= 0-31.
        Returns the PWM dutycycle.
        For normal PWM the dutycycle will be out of the defined range
        for the GPIO (see [*get_PWM_range*]).
        If a hardware clock is active on the GPIO the reported
        dutycycle will be 500000 (500k) out of 1000000 (1M).
        If hardware PWM is active on the GPIO the reported dutycycle
        will be out of a 1000000 (1M).
        ...
        pi.set_PWM_dutycycle(4, 25)
        print(pi.get_PWM_dutycycle(4))
        25
        pi.set_PWM_dutycycle(4, 203)
        print(pi.get_PWM_dutycycle(4))
        203
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_GDC, user_gpio, 0)
        return _u2i(res)
    
    async def set_PWM_range(self, user_gpio, range_):
        """
        Sets the range of PWM values to be used on the GPIO.
        user_gpio:= 0-31.
            range_:= 25-40000.
        ...
        pi.set_PWM_range(9, 100)  # now  25 1/4,   50 1/2,   75 3/4 on
        pi.set_PWM_range(9, 500)  # now 125 1/4,  250 1/2,  375 3/4 on
        pi.set_PWM_range(9, 3000) # now 750 1/4, 1500 1/2, 2250 3/4 on
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PRS, user_gpio, range_)
        return _u2i(res)
   
    async def get_PWM_range(self, user_gpio):
        """
        Returns the range of PWM values being used on the GPIO.
        user_gpio:= 0-31.
        If a hardware clock or hardware PWM is active on the GPIO
        the reported range will be 1000000 (1M).
        ...
        pi.set_PWM_range(9, 500)
        print(pi.get_PWM_range(9))
        500
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PRG, user_gpio, 0)
        return _u2i(res)
   
    async def get_PWM_real_range(self, user_gpio):
        """
        Returns the real (underlying) range of PWM values being
        used on the GPIO.
        user_gpio:= 0-31.
        If a hardware clock is active on the GPIO the reported
        real range will be 1000000 (1M).
        If hardware PWM is active on the GPIO the reported real range
        will be approximately 250M divided by the set PWM frequency.
        ...
        pi.set_PWM_frequency(4, 800)
        print(pi.get_PWM_real_range(4))
        250
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PRRG, user_gpio, 0)
        return _u2i(res)
   
    async def set_PWM_frequency(self, user_gpio, frequency):
        """
        Sets the frequency (in Hz) of the PWM to be used on the GPIO.
        user_gpio:= 0-31.
        frequency:= >=0 Hz
        Returns the numerically closest frequency if OK, otherwise
        PI_BAD_USER_GPIO or PI_NOT_PERMITTED.
        If PWM is currently active on the GPIO it will be switched
        off and then back on at the new frequency.
        Each GPIO can be independently set to one of 18 different
        PWM frequencies.
        The selectable frequencies depend upon the sample rate which
        may be 1, 2, 4, 5, 8, or 10 microseconds (default 5).  The
        sample rate is set when the pigpio daemon is started.
        The frequencies for each sample rate are:
        . .
                                Hertz
                1: 40000 20000 10000 8000 5000 4000 2500 2000 1600
                    1250  1000   800  500  400  250  200  100   50
                2: 20000 10000  5000 4000 2500 2000 1250 1000  800
                    625   500   400  250  200  125  100   50   25
                4: 10000  5000  2500 2000 1250 1000  625  500  400
                    313   250   200  125  100   63   50   25   13
        sample
        rate
        (us)  5:  8000  4000  2000 1600 1000  800  500  400  320
                    250   200   160  100   80   50   40   20   10
                8:  5000  2500  1250 1000  625  500  313  250  200
                    156   125   100   63   50   31   25   13    6
            10:  4000  2000  1000  800  500  400  250  200  160
                    125   100    80   50   40   25   20   10    5
        . .
        ...
        pi.set_PWM_frequency(4,0)
        print(pi.get_PWM_frequency(4))
        10
        pi.set_PWM_frequency(4,100000)
        print(pi.get_PWM_frequency(4))
        8000
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PFS, user_gpio, frequency)
        return _u2i(res)
  
    async def get_PWM_frequency(self, user_gpio):
        """
        Returns the frequency of PWM being used on the GPIO.
        user_gpio:= 0-31.
        Returns the frequency (in Hz) used for the GPIO.
        For normal PWM the frequency will be that defined for the GPIO
        by [*set_PWM_frequency*].
        If a hardware clock is active on the GPIO the reported frequency
        will be that set by [*hardware_clock*].
        If hardware PWM is active on the GPIO the reported frequency
        will be that set by [*hardware_PWM*].
        ...
        pi.set_PWM_frequency(4,0)
        print(pi.get_PWM_frequency(4))
        10
        pi.set_PWM_frequency(4, 800)
        print(pi.get_PWM_frequency(4))
        800
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_PFG, user_gpio, 0)
        return _u2i(res)
   
    async def hardware_clock(self, gpio, clkfreq):
        """
        Starts a hardware clock on a GPIO at the specified frequency.
        Frequencies above 30MHz are unlikely to work.
            gpio:= see description
        clkfreq:= 0 (off) or 4689-250M (13184-375M for the BCM2711)
        Returns 0 if OK, otherwise PI_NOT_PERMITTED, PI_BAD_GPIO,
        PI_NOT_HCLK_GPIO, PI_BAD_HCLK_FREQ,or PI_BAD_HCLK_PASS.
        The same clock is available on multiple GPIO.  The latest
        frequency setting will be used by all GPIO which share a clock.
        The GPIO must be one of the following:
        . .
        4   clock 0  All models
        5   clock 1  All models but A and B (reserved for system use)
        6   clock 2  All models but A and B
        20  clock 0  All models but A and B
        21  clock 1  All models but A and Rev.2 B (reserved for system use)
        32  clock 0  Compute module only
        34  clock 0  Compute module only
        42  clock 1  Compute module only (reserved for system use)
        43  clock 2  Compute module only
        44  clock 1  Compute module only (reserved for system use)
        . .
        Access to clock 1 is protected by a password as its use will
        likely crash the Pi.  The password is given by or'ing 0x5A000000
        with the GPIO number.
        ...
        pi.hardware_clock(4, 5000) # 5 KHz clock on GPIO 4
        pi.hardware_clock(4, 40000000) # 40 MHz clock on GPIO 4
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_HC, gpio, clkfreq)
        return _u2i(res)
    
    async def hardware_PWM(self, gpio, PWMfreq, PWMduty):
        """
        Starts hardware PWM on a GPIO at the specified frequency
        and dutycycle. Frequencies above 30MHz are unlikely to work.
        NOTE: Any waveform started by [*wave_send_once*],
        [*wave_send_repeat*], or [*wave_chain*] will be cancelled.
        This function is only valid if the pigpio main clock is PCM.
        The main clock defaults to PCM but may be overridden when the
        pigpio daemon is started (option -t).
            gpio:= see descripton
        PWMfreq:= 0 (off) or 1-125M (1-187.5M for the BCM2711).
        PWMduty:= 0 (off) to 1000000 (1M)(fully on).
        Returns 0 if OK, otherwise PI_NOT_PERMITTED, PI_BAD_GPIO,
        PI_NOT_HPWM_GPIO, PI_BAD_HPWM_DUTY, PI_BAD_HPWM_FREQ.
        The same PWM channel is available on multiple GPIO.
        The latest frequency and dutycycle setting will be used
        by all GPIO which share a PWM channel.
        The GPIO must be one of the following:
        . .
        12  PWM channel 0  All models but A and B
        13  PWM channel 1  All models but A and B
        18  PWM channel 0  All models
        19  PWM channel 1  All models but A and B
        40  PWM channel 0  Compute module only
        41  PWM channel 1  Compute module only
        45  PWM channel 1  Compute module only
        52  PWM channel 0  Compute module only
        53  PWM channel 1  Compute module only
        . .
        The actual number of steps beween off and fully on is the
        integral part of 250M/PWMfreq (375M/PWMfreq for the BCM2711).
        The actual frequency set is 250M/steps (375M/steps
        for the BCM2711).
        There will only be a million steps for a PWMfreq of 250
        (375 for the BCM2711). Lower frequencies will have more
        steps and higher frequencies will have fewer steps.
        PWMduty is automatically scaled to take this into account.
        ...
        pi.hardware_PWM(18, 800, 250000) # 800Hz 25% dutycycle
        pi.hardware_PWM(18, 2000, 750000) # 2000Hz 75% dutycycle
        ...
        """
        # pigpio message format

        # I p1 gpio
        # I p2 PWMfreq
        # I p3 4
        ## extension ##
        # I PWMdutycycle
        extents = [struct.pack("I", PWMduty)]
        res = await self._pigpio_aio_command_ext(_PI_CMD_HP, gpio, PWMfreq, 4, extents)
        return _u2i(res)   
    
    async def add_callback(self, user_gpio, edge=RISING_EDGE, func=None):
        """
        Calls a user supplied function (a callback) whenever the
        specified gpio edge is detected.

        user_gpio:= 0-31.
           edge:= EITHER_EDGE, RISING_EDGE (default), or FALLING_EDGE.
           func:= user supplied callback function.

        The user supplied callback receives three parameters, the gpio,
        the level, and the tick.

        If a user callback is not specified a default tally callback is
        provided which simply counts edges.  The count may be retrieved
        by calling the tally function.

        The callback may be cancelled by calling the cancel function.

        A gpio may have multiple callbacks (although I can't think of
        a reason to do so).

        ...
        def cbf(gpio, level, tick):
         print(gpio, level, tick)

        cb1 = pi.callback(22, pigpio.EITHER_EDGE, cbf)

        cb2 = pi.callback(4, pigpio.EITHER_EDGE)

        cb3 = pi.callback(17)

        print(cb3.tally())

        cb1.cancel() # To cancel callback cb1.
        ...
        """

        cb = Callback(self._notify, user_gpio, edge, func)
        await self._notify.append(cb)

        return cb

    async def notify_open(self):
        """
        Returns a notification handle (>=0).

        A notification is a method for being notified of GPIO state
        changes via a pipe.

        Pipes are only accessible from the local machine so this
        function serves no purpose if you are using Python from a
        remote machine.  The in-built (socket) notifications
        provided by [*callback*] should be used instead.

        Notifications for handle x will be available at the pipe
        named /dev/pigpiox (where x is the handle number).

        E.g. if the function returns 15 then the notifications must be
        read from /dev/pigpio15.

        Notifications have the following structure:

        . .
        H seqno
        H flags
        I tick
        I level
        . .

        seqno: starts at 0 each time the handle is opened and then
        increments by one for each report.

        flags: three flags are defined, PI_NTFY_FLAGS_WDOG,
        PI_NTFY_FLAGS_ALIVE, and PI_NTFY_FLAGS_EVENT.

        If bit 5 is set (PI_NTFY_FLAGS_WDOG) then bits 0-4 of the
        flags indicate a GPIO which has had a watchdog timeout.

        If bit 6 is set (PI_NTFY_FLAGS_ALIVE) this indicates a keep
        alive signal on the pipe/socket and is sent once a minute
        in the absence of other notification activity.

        If bit 7 is set (PI_NTFY_FLAGS_EVENT) then bits 0-4 of the
        flags indicate an event which has been triggered.


        tick: the number of microseconds since system boot.  It wraps
        around after 1h12m.

        level: indicates the level of each GPIO.  If bit 1<<x is set
        then GPIO x is high.

        ...
        h = pi.notify_open()
        if h >= 0:
            pi.notify_begin(h, 1234)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_NO, 0, 0)
        return _u2i(res)

    async def notify_begin(self, handle, bits):
        """
        Starts notifications on a handle.

        handle:= >=0 (as returned by a prior call to [*notify_open*])
        bits:= a 32 bit mask indicating the GPIO to be notified.

        The notification sends state changes for each GPIO whose
        corresponding bit in bits is set.

        The following code starts notifications for GPIO 1, 4,
        6, 7, and 10 (1234 = 0x04D2 = 0b0000010011010010).

        ...
        h = pi.notify_open()
        if h >= 0:
            pi.notify_begin(h, 1234)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_NB, handle, bits)
        return _u2i(res)
 
    async def notify_pause(self, handle):
        """
        Pauses notifications on a handle.

        handle:= >=0 (as returned by a prior call to [*notify_open*])

        Notifications for the handle are suspended until
        [*notify_begin*] is called again.

        ...
        h = pi.notify_open()
        if h >= 0:
            pi.notify_begin(h, 1234)
            ...
            pi.notify_pause(h)
            ...
            pi.notify_begin(h, 1234)
            ...
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_NP, handle, 0)
        return _u2i(res)

    async def notify_close(self, handle):
        """
        Stops notifications on a handle and releases the handle for reuse.

        handle:= >=0 (as returned by a prior call to [*notify_open*])

        ...
        h = pi.notify_open()
        if h >= 0:
            pi.notify_begin(h, 1234)
            ...
            pi.notify_close(h)
            ...
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_NC, handle, 0)
        return _u2i(res)
    
    async def set_servo_pulsewidth(self, user_gpio, pulsewidth):
        """
        Starts (500-2500) or stops (0) servo pulses on the GPIO.
         user_gpio:= 0-31.
        pulsewidth:= 0 (off),
                     500 (most anti-clockwise) - 2500 (most clockwise).
        The selected pulsewidth will continue to be transmitted until
        changed by a subsequent call to set_servo_pulsewidth.
        The pulsewidths supported by servos varies and should probably
        be determined by experiment. A value of 1500 should always be
        safe and represents the mid-point of rotation.
        You can DAMAGE a servo if you command it to move beyond its
        limits.
        ...
        await pi.set_servo_pulsewidth(17, 0)    # off
        await pi.set_servo_pulsewidth(17, 1000) # safe anti-clockwise
        await pi.set_servo_pulsewidth(17, 1500) # centre
        await pi.set_servo_pulsewidth(17, 2000) # safe clockwise
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_SERVO, user_gpio, int(pulsewidth))
        return _u2i(res)
    
    async def wave_clear(self):
        """
        Clears all waveforms and any data added by calls to the
        [*wave_add_**] functions.

        ...
        pi.wave_clear()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVCLR, 0, 0)
        return _u2i(res)

    async def wave_add_new(self):
        """
        Starts a new empty waveform.

        You would not normally need to call this function as it is
        automatically called after a waveform is created with the
        [*wave_create*] function.

        ...
        pi.wave_add_new()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVNEW, 0, 0)
        return _u2i(res)

    async def wave_add_generic(self, pulses):
        """
        Adds a list of pulses to the current waveform.

        pulses:= list of pulses to add to the waveform.

        Returns the new total number of pulses in the current waveform.

        The pulses are interleaved in time order within the existing
        waveform (if any).

        Merging allows the waveform to be built in parts, that is the
        settings for GPIO#1 can be added, and then GPIO#2 etc.

        If the added waveform is intended to start after or within
        the existing waveform then the first pulse should consist
        solely of a delay.

        ...
        G1=4
        G2=24

        pi.set_mode(G1, pigpio.OUTPUT)
        pi.set_mode(G2, pigpio.OUTPUT)

        flash_500=[] # flash every 500 ms
        flash_100=[] # flash every 100 ms

        #                              ON     OFF  DELAY

        flash_500.append(pigpio.pulse(1<<G1, 1<<G2, 500000))
        flash_500.append(pigpio.pulse(1<<G2, 1<<G1, 500000))

        flash_100.append(pigpio.pulse(1<<G1, 1<<G2, 100000))
        flash_100.append(pigpio.pulse(1<<G2, 1<<G1, 100000))

        pi.wave_clear() # clear any existing waveforms

        pi.wave_add_generic(flash_500) # 500 ms flashes
        f500 = pi.wave_create() # create and save id

        pi.wave_add_generic(flash_100) # 100 ms flashes
        f100 = pi.wave_create() # create and save id

        pi.wave_send_repeat(f500)

        time.sleep(4)

        pi.wave_send_repeat(f100)

        time.sleep(4)

        pi.wave_send_repeat(f500)

        time.sleep(4)

        pi.wave_tx_stop() # stop waveform

        pi.wave_clear() # clear all waveforms
        ...
        """
        # pigpio message format

        # I p1 0
        # I p2 0
        # I p3 pulses * 12
        ## extension ##
        # III on/off/delay * pulses
        if len(pulses):
           ext = bytearray()
           for p in pulses:
              ext.extend(struct.pack("III", p.gpio_on, p.gpio_off, p.delay))
           extents = [ext]
           res = await self._pigpio_aio_command_ext(
              _PI_CMD_WVAG, 0, 0, len(pulses)*12, extents)
           return _u2i(res)
        else:
           return 0

    async def wave_add_serial(
        self, user_gpio, baud, data, offset=0, bb_bits=8, bb_stop=2):
        """
        Adds a waveform representing serial data to the existing
        waveform (if any).  The serial data starts [*offset*]
        microseconds from the start of the waveform.

        user_gpio:= GPIO to transmit data.  You must set the GPIO mode
                    to output.
             baud:= 50-1000000 bits per second.
             data:= the bytes to write.
           offset:= number of microseconds from the start of the
                    waveform, default 0.
          bb_bits:= number of data bits, default 8.
          bb_stop:= number of stop half bits, default 2.

        Returns the new total number of pulses in the current waveform.

        The serial data is formatted as one start bit, [*bb_bits*]
        data bits, and [*bb_stop*]/2 stop bits.

        It is legal to add serial data streams with different baud
        rates to the same waveform.

        The bytes required for each character depend upon [*bb_bits*].

        For [*bb_bits*] 1-8 there will be one byte per character.
        For [*bb_bits*] 9-16 there will be two bytes per character.
        For [*bb_bits*] 17-32 there will be four bytes per character.

        ...
        pi.wave_add_serial(4, 300, 'Hello world')

        pi.wave_add_serial(4, 300, b"Hello world")

        pi.wave_add_serial(4, 300, b'\\x23\\x01\\x00\\x45')

        pi.wave_add_serial(17, 38400, [23, 128, 234], 5000)
        ...
        """
        # pigpio message format

        # I p1 gpio
        # I p2 baud
        # I p3 len+12
        ## extension ##
        # I bb_bits
        # I bb_stop
        # I offset
        # s len data bytes
        if len(data):
           extents = [struct.pack("III", bb_bits, bb_stop, offset), data]
           res = await self._pigpio_aio_command_ext(
              _PI_CMD_WVAS, user_gpio, baud, len(data)+12, extents)
           return _u2i(res)
        else:
           return 0

    async def wave_create(self):
        """
        Creates a waveform from the data provided by the prior calls
        to the [*wave_add_**] functions.

        Returns a wave id (>=0) if OK,  otherwise PI_EMPTY_WAVEFORM,
        PI_TOO_MANY_CBS, PI_TOO_MANY_OOL, or PI_NO_WAVEFORM_ID.

        The data provided by the [*wave_add_**] functions is consumed by
        this function.

        As many waveforms may be created as there is space available.
        The wave id is passed to [*wave_send_**] to specify the waveform
        to transmit.

        Normal usage would be

        Step 1. [*wave_clear*] to clear all waveforms and added data.

        Step 2. [*wave_add_**] calls to supply the waveform data.

        Step 3. [*wave_create*] to create the waveform and get a unique id

        Repeat steps 2 and 3 as needed.

        Step 4. [*wave_send_**] with the id of the waveform to transmit.

        A waveform comprises one or more pulses.

        A pulse specifies

        1) the GPIO to be switched on at the start of the pulse.
        2) the GPIO to be switched off at the start of the pulse.
        3) the delay in microseconds before the next pulse.

        Any or all the fields can be zero.  It doesn't make any sense
        to set all the fields to zero (the pulse will be ignored).

        When a waveform is started each pulse is executed in order with
        the specified delay between the pulse and the next.

        ...
        wid = pi.wave_create()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVCRE, 0, 0)
        return _u2i(res)

    async def wave_create_and_pad(self, percent):
        """
        This function creates a waveform like [*wave_create*] but pads the consumed
        resources. Where percent gives the percentage of the resources to use
        (in terms of the theoretical maximum, not the current amount free).
        This allows the reuse of deleted waves while a transmission is active.

        Upon success a wave id greater than or equal to 0 is returned, otherwise
        PI_EMPTY_WAVEFORM, PI_TOO_MANY_CBS, PI_TOO_MANY_OOL, or PI_NO_WAVEFORM_ID.

        . .
        percent: 0-100, size of waveform as percentage of maximum available.
        . .

        The data provided by the [*wave_add_**] functions are consumed by this
        function.

        As many waveforms may be created as there is space available. The
        wave id is passed to [*wave_send_**] to specify the waveform to transmit.

        A usage would be the creation of two waves where one is filled while the
        other is being transmitted.  Each wave is assigned 50% of the resources.
        This buffer structure allows the transmission of infinite wave sequences.

        Normal usage:

        Step 1. [*wave_clear*] to clear all waveforms and added data.

        Step 2. [*wave_add_**] calls to supply the waveform data.

        Step 3. [*wave_create_and_pad*] to create a waveform of uniform size.

        Step 4. [*wave_send_**] with the id of the waveform to transmit.

        Repeat steps 2-4 as needed.

        Step 5. Any wave id can now be deleted and another wave of the same size
                can be created in its place.

        ...
        wid = pi.wave_create_and_pad(50)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVCAP, percent, 0)
        return _u2i(res)

    async def wave_delete(self, wave_id):
        """
        This function deletes the waveform with id wave_id.

        wave_id:= >=0 (as returned by a prior call to [*wave_create*]).

        Wave ids are allocated in order, 0, 1, 2, etc.

        The wave is flagged for deletion.  The resources used by the wave
        will only be reused when either of the following apply.

        - all waves with higher numbered wave ids have been deleted or have
        been flagged for deletion.

        - a new wave is created which uses exactly the same resources as
        the current wave (see the C source for gpioWaveCreate for details).

        ...
        pi.wave_delete(6) # delete waveform with id 6

        pi.wave_delete(0) # delete waveform with id 0
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVDEL, wave_id, 0)
        return _u2i(res)

    async def wave_tx_start(self): # DEPRECATED
        """
        This function is deprecated and has been removed.

        Use [*wave_create*]/[*wave_send_**] instead.
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVGO, 0, 0)
        return _u2i(res)

    async def wave_tx_repeat(self): # DEPRECATED
        """
        This function is deprecated and has beeen removed.

        Use [*wave_create*]/[*wave_send_**] instead.
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVGOR, 0, 0)
        return _u2i(res)

    async def wave_send_once(self, wave_id):
        """
        Transmits the waveform with id wave_id.  The waveform is sent
        once.

        NOTE: Any hardware PWM started by [*hardware_PWM*] will
        be cancelled.

        wave_id:= >=0 (as returned by a prior call to [*wave_create*]).

        Returns the number of DMA control blocks used in the waveform.

        ...
        cbs = pi.wave_send_once(wid)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVTX, wave_id, 0)
        return _u2i(res)

    async def wave_send_repeat(self, wave_id):
        """
        Transmits the waveform with id wave_id.  The waveform repeats
        until wave_tx_stop is called or another call to [*wave_send_**]
        is made.

        NOTE: Any hardware PWM started by [*hardware_PWM*] will
        be cancelled.

        wave_id:= >=0 (as returned by a prior call to [*wave_create*]).

        Returns the number of DMA control blocks used in the waveform.

        ...
        cbs = pi.wave_send_repeat(wid)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVTXR, wave_id, 0)
        return _u2i(res)

    async def wave_send_using_mode(self, wave_id, mode):
        """
        Transmits the waveform with id wave_id using mode mode.

        wave_id:= >=0 (as returned by a prior call to [*wave_create*]).
           mode:= WAVE_MODE_ONE_SHOT, WAVE_MODE_REPEAT,
                  WAVE_MODE_ONE_SHOT_SYNC, or WAVE_MODE_REPEAT_SYNC.

        WAVE_MODE_ONE_SHOT: same as [*wave_send_once*].

        WAVE_MODE_REPEAT same as [*wave_send_repeat*].

        WAVE_MODE_ONE_SHOT_SYNC same as [*wave_send_once*] but tries
        to sync with the previous waveform.

        WAVE_MODE_REPEAT_SYNC same as [*wave_send_repeat*] but tries
        to sync with the previous waveform.

        WARNING: bad things may happen if you delete the previous
        waveform before it has been synced to the new waveform.

        NOTE: Any hardware PWM started by [*hardware_PWM*] will
        be cancelled.

        wave_id:= >=0 (as returned by a prior call to [*wave_create*]).

        Returns the number of DMA control blocks used in the waveform.

        ...
        cbs = pi.wave_send_using_mode(wid, WAVE_MODE_REPEAT_SYNC)
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVTXM, wave_id, mode)
        return _u2i(res)

    async def wave_tx_at(self):
        """
        Returns the id of the waveform currently being
        transmitted using [*wave_send**].  Chained waves are not supported.

        Returns the waveform id or one of the following special
        values:

        WAVE_NOT_FOUND (9998) - transmitted wave not found.
        NO_TX_WAVE (9999) - no wave being transmitted.

        ...
        wid = pi.wave_tx_at()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVTAT, 0, 0)
        return _u2i(res)

    async def wave_tx_busy(self):
        """
        Returns 1 if a waveform is currently being transmitted,
        otherwise 0.

        ...
        pi.wave_send_once(0) # send first waveform

        while pi.wave_tx_busy(): # wait for waveform to be sent
           time.sleep(0.1)

        pi.wave_send_once(1) # send next waveform
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVBSY, 0, 0)
        return _u2i(res)

    async def wave_tx_stop(self):
        """
        Stops the transmission of the current waveform.

        This function is intended to stop a waveform started with
        wave_send_repeat.

        ...
        pi.wave_send_repeat(3)

        time.sleep(5)

        pi.wave_tx_stop()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVHLT, 0, 0)
        return _u2i(res)

    async def wave_chain(self, data):
        """
        This function transmits a chain of waveforms.

        NOTE: Any hardware PWM started by [*hardware_PWM*]
        will be cancelled.

        The waves to be transmitted are specified by the contents
        of data which contains an ordered list of [*wave_id*]s
        and optional command codes and related data.

        Returns 0 if OK, otherwise PI_CHAIN_NESTING,
        PI_CHAIN_LOOP_CNT, PI_BAD_CHAIN_LOOP, PI_BAD_CHAIN_CMD,
        PI_CHAIN_COUNTER, PI_BAD_CHAIN_DELAY, PI_CHAIN_TOO_BIG,
        or PI_BAD_WAVE_ID.

        Each wave is transmitted in the order specified.  A wave
        may occur multiple times per chain.

        A blocks of waves may be transmitted multiple times by
        using the loop commands. The block is bracketed by loop
        start and end commands.  Loops may be nested.

        Delays between waves may be added with the delay command.

        The following command codes are supported:

        Name         @ Cmd & Data @ Meaning
        Loop Start   @ 255 0      @ Identify start of a wave block
        Loop Repeat  @ 255 1 x y  @ loop x + y*256 times
        Delay        @ 255 2 x y  @ delay x + y*256 microseconds
        Loop Forever @ 255 3      @ loop forever

        If present Loop Forever must be the last entry in the chain.

        The code is currently dimensioned to support a chain with
        roughly 600 entries and 20 loop counters.

        ...
        #!/usr/bin/env python

        import time
        import pigpio

        WAVES=5
        GPIO=4

        wid=[0]*WAVES

        pi = pigpio.pi() # Connect to local Pi.

        pi.set_mode(GPIO, pigpio.OUTPUT);

        for i in range(WAVES):
           pi.wave_add_generic([
              pigpio.pulse(1<<GPIO, 0, 20),
              pigpio.pulse(0, 1<<GPIO, (i+1)*200)]);

           wid[i] = pi.wave_create();

        pi.wave_chain([
           wid[4], wid[3], wid[2],       # transmit waves 4+3+2
           255, 0,                       # loop start
              wid[0], wid[0], wid[0],    # transmit waves 0+0+0
              255, 0,                    # loop start
                 wid[0], wid[1],         # transmit waves 0+1
                 255, 2, 0x88, 0x13,     # delay 5000us
              255, 1, 30, 0,             # loop end (repeat 30 times)
              255, 0,                    # loop start
                 wid[2], wid[3], wid[0], # transmit waves 2+3+0
                 wid[3], wid[1], wid[2], # transmit waves 3+1+2
              255, 1, 10, 0,             # loop end (repeat 10 times)
           255, 1, 5, 0,                 # loop end (repeat 5 times)
           wid[4], wid[4], wid[4],       # transmit waves 4+4+4
           255, 2, 0x20, 0x4E,           # delay 20000us
           wid[0], wid[0], wid[0],       # transmit waves 0+0+0
           ])

        while pi.wave_tx_busy():
           time.sleep(0.1);

        for i in range(WAVES):
           pi.wave_delete(wid[i])

        pi.stop()
        ...
        """
        # I p1 0
        # I p2 0
        # I p3 len
        ## extension ##
        # s len data bytes

        res = await self._pigpio_aio_command_ext(
           _PI_CMD_WVCHA, 0, 0, len(data), [data])
        return _u2i(res)

    async def wave_get_micros(self):
        """
        Returns the length in microseconds of the current waveform.

        ...
        micros = pi.wave_get_micros()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVSM, 0, 0)
        return _u2i(res)

    async def wave_get_max_micros(self):
        """
        Returns the maximum possible size of a waveform in microseconds.

        ...
        micros = pi.wave_get_max_micros()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVSM, 2, 0)
        return _u2i(res)

    async def wave_get_pulses(self):
        """
        Returns the length in pulses of the current waveform.

        ...
        pulses = pi.wave_get_pulses()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVSP, 0, 0)
        return _u2i(res)

    async def wave_get_max_pulses(self):
        """
        Returns the maximum possible size of a waveform in pulses.

        ...
        pulses = pi.wave_get_max_pulses()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVSP, 2, 0)
        return _u2i(res)

    async def wave_get_cbs(self):
        """
        Returns the length in DMA control blocks of the current
        waveform.

        ...
        cbs = pi.wave_get_cbs()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVSC, 0, 0)
        return _u2i(res)

    async def wave_get_max_cbs(self):
        """
        Returns the maximum possible size of a waveform in DMA
        control blocks.

        ...
        cbs = pi.wave_get_max_cbs()
        ...
        """
        res = await self._pigpio_aio_command(_PI_CMD_WVSC, 2, 0)
        return _u2i(res)

    async def i2c_open(self, bus, address):
        """Open an i2c device on a bus."""
        res = await self._pigpio_aio_command(_PI_CMD_I2CO, int(bus), int(address))
        return _u2i(res)
    
    async def i2c_close(self, handle):
        """Close an i2c handle."""
        res = await self._pigpio_aio_command(_PI_CMD_I2CC, handle)
        return _u2i(res)
   
    async def i2c_write_byte_data(self, handle, register, data):
        """Write byte to i2c register on handle."""
        extents = [struct.pack("I", data)]
        res = await self._pigpio_aio_command_ext(_PI_CMD_I2CWB, handle, int(register), 4, extents)
        return _u2i(res)
   
    async def _rxbuf(self, count):
        """"Returns count bytes from the command socket."""
        ext = await self._loop.sock_recv(self.s, count)
        while len(ext) < count:
            ext.extend((await self._loop.sock_recv(self.s, count - len(ext))))
        return ext
    
    async def i2c_read_byte_data(self, handle, register):
        """Write byte to i2c register on handle."""
        res = await self._pigpio_aio_command(_PI_CMD_I2CRB, handle, int(register))
        return _u2i(res)
   
    async def i2c_read_i2c_block_data(self, handle, register, count):
        """Read count bytes from an i2c handle."""
        extents = [struct.pack("I", count)]
        async with self._lock:
            bytes = await self._pigpio_aio_command_ext_unlocked(_PI_CMD_I2CRI, handle, int(register), 4, extents)
            if bytes > 0:
                data = await self._rxbuf(count)
            else:
                data = ""
        return data

    def __init__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self.s = None
        self._notify = _callback_handler(self)
        self._lock = asyncio.Lock()
