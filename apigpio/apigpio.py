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

_PI_CMD_NOIB = 99

_PI_CMD_BI2CC = 89
_PI_CMD_BI2CO = 90
_PI_CMD_BI2CZ = 91

_PI_CMD_I2CZ = 92

_PI_CMD_WVCHA = 93

_PI_CMD_SLRI = 94

# pigpio error text

_errors = [
   [PI_INIT_FAILED      , "pigpio initialisation failed"],
   [PI_BAD_USER_GPIO     , "gpio not 0-31"],
   [PI_BAD_GPIO          , "gpio not 0-53"],
   [PI_BAD_MODE          , "mode not 0-7"],
   [PI_BAD_LEVEL         , "level not 0-1"],
   [PI_BAD_PUD           , "pud not 0-2"],
   [PI_BAD_PULSEWIDTH    , "pulsewidth not 0 or 500-2500"],
   [PI_BAD_DUTYCYCLE     , "dutycycle not 0-range (default 255)"],
   [PI_BAD_TIMER        , "timer not 0-9"],
   [PI_BAD_MS           , "ms not 10-60000"],
   [PI_BAD_TIMETYPE     , "timetype not 0-1"],
   [PI_BAD_SECONDS      , "seconds < 0"],
   [PI_BAD_MICROS       , "micros not 0-999999"],
   [PI_TIMER_FAILED     , "gpioSetTimerFunc failed"],
   [PI_BAD_WDOG_TIMEOUT  , "timeout not 0-60000"],
   [PI_NO_ALERT_FUNC    , "DEPRECATED"],
   [PI_BAD_CLK_PERIPH   , "clock peripheral not 0-1"],
   [PI_BAD_CLK_SOURCE   , "DEPRECATED"],
   [PI_BAD_CLK_MICROS   , "clock micros not 1, 2, 4, 5, 8, or 10"],
   [PI_BAD_BUF_MILLIS   , "buf millis not 100-10000"],
   [PI_BAD_DUTYRANGE     , "dutycycle range not 25-40000"],
   [PI_BAD_SIGNUM       , "signum not 0-63"],
   [PI_BAD_PATHNAME     , "can't open pathname"],
   [PI_NO_HANDLE         , "no handle available"],
   [PI_BAD_HANDLE        , "unknown handle"],
   [PI_BAD_IF_FLAGS     , "ifFlags > 3"],
   [PI_BAD_CHANNEL      , "DMA channel not 0-14"],
   [PI_BAD_SOCKET_PORT  , "socket port not 1024-30000"],
   [PI_BAD_FIFO_COMMAND , "unknown fifo command"],
   [PI_BAD_SECO_CHANNEL , "DMA secondary channel not 0-6"],
   [PI_NOT_INITIALISED  , "function called before gpioInitialise"],
   [PI_INITIALISED      , "function called after gpioInitialise"],
   [PI_BAD_WAVE_MODE    , "waveform mode not 0-1"],
   [PI_BAD_CFG_INTERNAL , "bad parameter in gpioCfgInternals call"],
   [PI_BAD_WAVE_BAUD     , "baud rate not 50-250000(RX)/1000000(TX)"],
   [PI_TOO_MANY_PULSES   , "waveform has too many pulses"],
   [PI_TOO_MANY_CHARS    , "waveform has too many chars"],
   [PI_NOT_SERIAL_GPIO   , "no bit bang serial read in progress on gpio"],
   [PI_NOT_PERMITTED     , "no permission to update gpio"],
   [PI_SOME_PERMITTED    , "no permission to update one or more gpios"],
   [PI_BAD_WVSC_COMMND   , "bad WVSC subcommand"],
   [PI_BAD_WVSM_COMMND   , "bad WVSM subcommand"],
   [PI_BAD_WVSP_COMMND   , "bad WVSP subcommand"],
   [PI_BAD_PULSELEN      , "trigger pulse length not 1-100"],
   [PI_BAD_SCRIPT        , "invalid script"],
   [PI_BAD_SCRIPT_ID     , "unknown script id"],
   [PI_BAD_SER_OFFSET    , "add serial data offset > 30 minute"],
   [PI_GPIO_IN_USE       , "gpio already in use"],
   [PI_BAD_SERIAL_COUNT  , "must read at least a byte at a time"],
   [PI_BAD_PARAM_NUM     , "script parameter id not 0-9"],
   [PI_DUP_TAG           , "script has duplicate tag"],
   [PI_TOO_MANY_TAGS     , "script has too many tags"],
   [PI_BAD_SCRIPT_CMD    , "illegal script command"],
   [PI_BAD_VAR_NUM       , "script variable id not 0-149"],
   [PI_NO_SCRIPT_ROOM    , "no more room for scripts"],
   [PI_NO_MEMORY         , "can't allocate temporary memory"],
   [PI_SOCK_READ_FAILED  , "socket read failed"],
   [PI_SOCK_WRIT_FAILED  , "socket write failed"],
   [PI_TOO_MANY_PARAM    , "too many script parameters (> 10)"],
   [PI_NOT_HALTED        , "script already running or failed"],
   [PI_BAD_TAG           , "script has unresolved tag"],
   [PI_BAD_MICS_DELAY    , "bad MICS delay (too large)"],
   [PI_BAD_MILS_DELAY    , "bad MILS delay (too large)"],
   [PI_BAD_WAVE_ID       , "non existent wave id"],
   [PI_TOO_MANY_CBS      , "No more CBs for waveform"],
   [PI_TOO_MANY_OOL      , "No more OOL for waveform"],
   [PI_EMPTY_WAVEFORM    , "attempt to create an empty waveform"],
   [PI_NO_WAVEFORM_ID    , "No more waveform ids"],
   [PI_I2C_OPEN_FAILED   , "can't open I2C device"],
   [PI_SER_OPEN_FAILED   , "can't open serial device"],
   [PI_SPI_OPEN_FAILED   , "can't open SPI device"],
   [PI_BAD_I2C_BUS       , "bad I2C bus"],
   [PI_BAD_I2C_ADDR      , "bad I2C address"],
   [PI_BAD_SPI_CHANNEL   , "bad SPI channel"],
   [PI_BAD_FLAGS         , "bad i2c/spi/ser open flags"],
   [PI_BAD_SPI_SPEED     , "bad SPI speed"],
   [PI_BAD_SER_DEVICE    , "bad serial device name"],
   [PI_BAD_SER_SPEED     , "bad serial baud rate"],
   [PI_BAD_PARAM         , "bad i2c/spi/ser parameter"],
   [PI_I2C_WRITE_FAILED  , "I2C write failed"],
   [PI_I2C_READ_FAILED   , "I2C read failed"],
   [PI_BAD_SPI_COUNT     , "bad SPI count"],
   [PI_SER_WRITE_FAILED  , "ser write failed"],
   [PI_SER_READ_FAILED   , "ser read failed"],
   [PI_SER_READ_NO_DATA  , "ser read no data available"],
   [PI_UNKNOWN_COMMAND   , "unknown command"],
   [PI_SPI_XFER_FAILED   , "SPI xfer/read/write failed"],
   [PI_BAD_POINTER      , "bad (NULL) pointer"],
   [PI_NO_AUX_SPI        , "need a A+/B+/Pi2 for auxiliary SPI"],
   [PI_NOT_PWM_GPIO      , "gpio is not in use for PWM"],
   [PI_NOT_SERVO_GPIO    , "gpio is not in use for servo pulses"],
   [PI_NOT_HCLK_GPIO     , "gpio has no hardware clock"],
   [PI_NOT_HPWM_GPIO     , "gpio has no hardware PWM"],
   [PI_BAD_HPWM_FREQ     , "hardware PWM frequency not 1-125M"],
   [PI_BAD_HPWM_DUTY     , "hardware PWM dutycycle not 0-1M"],
   [PI_BAD_HCLK_FREQ     , "hardware clock frequency not 4689-250M"],
   [PI_BAD_HCLK_PASS     , "need password to use hardware clock 1"],
   [PI_HPWM_ILLEGAL      , "illegal, PWM in use for main clock"],
   [PI_BAD_DATABITS      , "serial data bits not 1-32"],
   [PI_BAD_STOPBITS      , "serial (half) stop bits not 2-8"],
   [PI_MSG_TOOBIG        , "socket/pipe message too big"],
   [PI_BAD_MALLOC_MODE   , "bad memory allocation mode"],
   [PI_TOO_MANY_SEGS    , "too many I2C transaction segments"],
   [PI_BAD_I2C_SEG      , "an I2C transaction segment failed"],
   [PI_BAD_SMBUS_CMD     , "SMBus command not supported"],
   [PI_NOT_I2C_GPIO      , "no bit bang I2C in progress on gpio"],
   [PI_BAD_I2C_WLEN      , "bad I2C write length"],
   [PI_BAD_I2C_RLEN      , "bad I2C read length"],
   [PI_BAD_I2C_CMD       , "bad I2C command"],
   [PI_BAD_I2C_BAUD      , "bad I2C baud rate, not 50-500k"],
   [PI_CHAIN_LOOP_CNT    , "bad chain loop count"],
   [PI_BAD_CHAIN_LOOP    , "empty chain loop"],
   [PI_CHAIN_COUNTER     , "too many chain counters"],
   [PI_BAD_CHAIN_CMD     , "bad chain command"],
   [PI_BAD_CHAIN_DELAY   , "bad chain delay micros"],
   [PI_CHAIN_NESTING     , "chain counters nested too deeply"],
   [PI_CHAIN_TOO_BIG     , "chain is too long"],
   [PI_DEPRECATED        , "deprecated function removed"],
   [PI_BAD_SER_INVERT    , "bit bang serial invert not 0 or 1"],
]


class error(Exception):
    """pigpio module exception"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def error_text(errnum):
    """
    Returns a text description of a pigpio error.

    errnum:= <0, the error number

    ...
    print(pigpio.error_text(-5))
    level not 0-1
    ...
    """
    for e in _errors:
        if e[0] == errnum:
            return e[1]
    return "unknown error ({})".format(errnum)


# A couple of hacks to cope with different string handling
# between various Python versions
# 3 != 2.7.8 != 2.7.3
# fixme : remove as we only support 3.4+

if sys.hexversion < 0x03000000:
    def _b(x):
        return x
else:
    def _b(x):
        return x.encode('latin-1')

if sys.hexversion < 0x02070800:
    def _str(x):
        return buffer(x)
else:
    def _str(x):
        return x


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
            raise error(error_text(v))
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
        self.func = func
        self.bit = 1 << gpio


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

    @asyncio.coroutine
    def _connect(self, address):

        # FIXME: duplication with pi.connect
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Disable the Nagle algorithm.
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.setblocking(False)

        # TODO: handle connection errors !
        yield from self._loop.sock_connect(self.s, address)

        self.handle = yield from self._pigpio_aio_command(_PI_CMD_NOIB, 0, 0)
        asyncio.async(self._wait_for_notif())

    @asyncio.coroutine
    def _wait_for_notif(self):

        # TODO: handle stop !
        while True:

            lastLevel = 0
            MSG_SIZ = 12
            buf = yield from self._loop.sock_recv(self.s, MSG_SIZ)

            while len(buf) < MSG_SIZ:
                yield from self._loop.sock_recv(self.s, MSG_SIZ-len(buf))

            seq, flags, tick, level = (struct.unpack('HHII', buf))
            if flags == 0:
                changed = level ^ lastLevel
                lastLevel = level
                for cb in self.callbacks:
                    if cb.bit & changed:
                        newLevel = 0
                        if cb.bit & level:
                            newLevel = 1
                        if (cb.edge ^ newLevel):
                            cb.func(cb.gpio, newLevel, tick)
                else:
                    if flags & NTFY_FLAGS_WDOG:
                        gpio = flags & NTFY_FLAGS_GPIO
                        for cb in self.callbacks:
                            if cb.gpio == gpio:
                                cb.func(cb.gpio, TIMEOUT, tick)

    @asyncio.coroutine
    def append(self, cb):
        """Adds a callback."""
        self.callbacks.append(cb.callb)
        self.monitor = self.monitor | cb.callb.bit

        #FIXMe asyncio.async(self.pi._pigpio_aio_command(_PI_CMD_NB, self.handle, self.monitor))
        yield from self.pi._pigpio_aio_command( _PI_CMD_NB, self.handle, self.monitor)

    @asyncio.coroutine
    def _pigpio_aio_command(self, cmd,  p1, p2,):
        # FIXME: duplication with pi._pigpio_aio_command
        data = struct.pack('IIII', cmd, p1, p2, 0)
        self._loop.sock_sendall(self.s, data)
        response = yield from self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res


class _callback:
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
        # FIXME yield from self._notify.append(self.callb)

    def cancel(self):
        """Cancels a callback by removing it from the notification thread."""
        self._notify.remove(self.callb)

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

    @asyncio.coroutine
    def _pigpio_aio_command(self, cmd,  p1, p2,):
        """
        Runs a pigpio socket command.

        sl:= command socket and lock.
        cmd:= the command to be executed.
        p1:= command parameter 1 (if applicable).
         p2:=  command parameter 2 (if applicable).
        """
        data = struct.pack('IIII', cmd, p1, p2, 0)
        self._loop.sock_sendall(self.s, data)
        response = yield from self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res

    def _pigpio_command_ext(self, cmd, p1, p2, p3, extents, rl=True):
        """
        Runs an extended pigpio socket command.

            sl:= command socket and lock.
           cmd:= the command to be executed.
            p1:= command parameter 1 (if applicable).
            p2:= command parameter 2 (if applicable).
            p3:= total size in bytes of following extents
        extents:= additional data blocks
        """
        ext = bytearray(struct.pack('IIII', cmd, p1, p2, p3))
        for x in extents:
            if type(x) == type(""):
                ext.extend(_b(x))
            else:
                ext.extend(x)
        self._loop.sock_sendall(self.s, ext)
        response = yield from self._loop.sock_recv(self.s, 16)
        _, res = struct.unpack('12sI', response)
        return res

    @asyncio.coroutine
    def connect(self, address):
        """
        Connect to a remote or local gpiod daemon.
        :param address: a pair (address, port), the address must be already resolved (for example an ip address)
        :return:
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(False)
        # Disable the Nagle algorithm.
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        yield from self._loop.sock_connect(self.s, address)

        yield from self._notify._connect(address)

    @asyncio.coroutine
    def get_version(self):
        res = yield from self._pigpio_aio_command(_PI_CMD_PIGPV)
        print('version: {}'.format(res))

    @asyncio.coroutine
    def get_pigpio_version(self):
        """
        Returns the pigpio software version.

        ...
        v = pi.get_pigpio_version()
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_PIGPV, 0, 0)

    @asyncio.coroutine
    def store_script(self, script):
        """
        Store a script for later execution.

        script:= the script text as a series of bytes.

        Returns a >=0 script id if OK.

        ...
        sid = pi.store_script(
         b'tag 0 w 22 1 mils 100 w 22 0 mils 100 dcr p0 jp 0')
        ...
        """
        # I p1 0
        # I p2 0
        # I p3 len
        ## extension ##
        # s len data bytes
        if len(script):
            res = yield from self._pigpio_command_ext(_PI_CMD_PROC,0, 0,
                                                      len(script),
                                                      [script])
            return _u2i(res)
        else:
            return 0

    @asyncio.coroutine
    def run_script(self, script_id, params=None):
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
        ## (optional) extension ##
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
        res = yield from self._pigpio_command_ext(_PI_CMD_PROCR, script_id,
                                                  0, nump*4, extents)
        return _u2i(res)


    def script_status(self, script_id):
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
        res = yield from self._pigpio_aio_command(_PI_CMD_PROCP, script_id, 0)
        bytes = u2i(res)

        if bytes > 0:

            # Fixme : this sould be the same a _rxbuf
            #data = self._rxbuf(bytes)
            data = yield from self._loop.sock_recv(self.s, bytes)
            while len(data) < bytes:
                b = yield from self._loop.sock_recv(self.s, bytes-len(data))
                data.extend(b)

            pars = struct.unpack('11i', _str(data))
            status = pars[0]
            params = pars[1:]
        else:
            status = bytes
            params = ()
        return status, params

    @asyncio.coroutine
    def stop_script(self, script_id):
        """
        Stops a running script.

        script_id:= id of stored script.

        ...
        status = pi.stop_script(sid)
        ...
        """
        res= yield from self._pigpio_aio_command(_PI_CMD_PROCS, script_id, 0)
        return _u2i(res)

    @asyncio.coroutine
    def delete_script(self, script_id):
        """
        Deletes a stored script.

        script_id:= id of stored script.

        ...
        status = pi.delete_script(sid)
        ...
        """
        res = yield from self._pigpio_aio_command( _PI_CMD_PROCD, script_id, 0)
        return _u2i(res)

    @asyncio.coroutine
    def read_bank_1(self):
        """
        Returns the levels of the bank 1 gpios (gpios 0-31).

        The returned 32 bit integer has a bit set if the corresponding
        gpio is high.  Gpio n has bit value (1<<n).

        ...
        print(bin(pi.read_bank_1()))
        0b10010100000011100100001001111
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_BR1, 0, 0)
        return res

    @asyncio.coroutine
    def clear_bank_1(self, bits):
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
        res= yield from self._pigpio_aio_command(_PI_CMD_BC1, bits, 0)
        return _u2i(res)

    def set_bank_1(self, bits):
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
        res = yield from self._pigpio_aio_command( _PI_CMD_BS1, bits, 0)
        return _u2i(res)

    @asyncio.coroutine
    def set_mode(self, gpio, mode):
        """
        Sets the gpio mode.

        gpio:= 0-53.
        mode:= INPUT, OUTPUT, ALT0, ALT1, ALT2, ALT3, ALT4, ALT5.

        ...
        pi.set_mode( 4, pigpio.INPUT)  # gpio  4 as input
        pi.set_mode(17, pigpio.OUTPUT) # gpio 17 as output
        pi.set_mode(24, pigpio.ALT2)   # gpio 24 as ALT2
        ...
        """
        res = yield from self._pigpio_aio_command(_PI_CMD_MODES, gpio, mode)
        return _u2i(res)

    @asyncio.coroutine
    def get_mode(self, gpio):
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
        res = yield from self._pigpio_aio_command(_PI_CMD_MODEG, gpio, 0)
        return _u2i(res)

    @asyncio.coroutine
    def write(self, gpio, level):
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
        res = yield from self._pigpio_aio_command(_PI_CMD_WRITE, gpio, level)
        return _u2i(res)

    @asyncio.coroutine
    def add_callback(self, user_gpio, edge=RISING_EDGE, func=None):
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

        cb = _callback(self._notify, user_gpio, edge, func)
        yield from self._notify.append(cb)

        return cb

    def __init__(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self.s = None
        self._notify = _callback_handler(self)
