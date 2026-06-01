import asyncio
from adafruit_motorkit import MotorKit


kit = MotorKit()

# ID used by adafruit motor HAT
TAIL_MOTOR = kit.motor3
HEAD_MOTOR = kit.motor2
MOUTH_MOTOR = kit.motor1


# -1 to flip, 1 to keep
FLIP_TAIL_DIR = -1
FLIP_MOUTH_DIR = -1
FLIP_HEAD_DIR = 0.9

# Dictionary to track timeout tasks for each motor
motor_timers = {
    "tail": None,
    "mouth": None,
    "head": None
}


async def _motor_timeout(timeout_seconds, motor_name):
    """Background task to turn off motor after timeout"""
    try:
        await asyncio.sleep(timeout_seconds)
        _motor_off(motor_name)
    except asyncio.CancelledError:
        # Task was cancelled, motor already stopped elsewhere
        pass


def motor_on(time_on_milisec, motor_name, direction):
    """Turns a motor on with an async timeout."""

    motor = HEAD_MOTOR
    flip = FLIP_HEAD_DIR

    if motor_name == "tail":
        motor = TAIL_MOTOR
        flip = FLIP_TAIL_DIR
    elif motor_name == "head":
        motor = HEAD_MOTOR
        flip = FLIP_HEAD_DIR
    elif motor_name == "mouth":
        motor = MOUTH_MOTOR
        flip = FLIP_MOUTH_DIR

    # Cancel any existing timeout task for this motor
    if motor_timers[motor_name]:
        motor_timers[motor_name].cancel()

    # Turn on the motor
    motor.throttle = 1.0 * direction * flip

    # Schedule an asyncio task to turn it off after the timeout
    timeout_seconds = time_on_milisec / 1000.0
    task = asyncio.create_task(_motor_timeout(timeout_seconds, motor_name))

    # Store the task so we can cancel it if needed
    motor_timers[motor_name] = task


def _motor_off(motor_name):
    """Power down the motor and clear its timeout task."""
    if motor_name == "tail":
        TAIL_MOTOR.throttle = 0.0
    elif motor_name == "head":
        HEAD_MOTOR.throttle = 0.0
    elif motor_name == "mouth":
        MOUTH_MOTOR.throttle = 0.0

    motor_timers[motor_name] = None


def motor_stop(motor_name):
    """Manually stop a motor and cancel its timeout task."""
    if motor_timers[motor_name]:
        motor_timers[motor_name].cancel()
        motor_timers[motor_name] = None

    _motor_off(motor_name)