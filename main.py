import asyncio
import json
import websockets
import time
from datetime import datetime
from motor_mgr import motor_on, motor_stop


# Track the current tasks so we can cancel them
current_thinking_task = None
current_listening_task = None


def log(message):
    """Print with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")


async def main():
    global current_thinking_task, current_listening_task

    log("Starting motor control system...")
    sleep_time = 10
    while True:
        try:
            async with websockets.connect("ws://localhost:6055") as ws:
                log("Connected to websocket server at ws://localhost:6055")

                async for raw in ws:
                    msg = json.loads(raw)
                    event = msg.get("event")
                    data = msg.get("data", {})
                    log(f"Event: {event}  data={data}")

                    # Ignore stt_text and thinking while actively listening
                    if current_listening_task and not current_listening_task.done():
                        if event in ["stt_text", "thinking"]:
                            log(f"→ Ignoring '{event}' while listening")
                            continue

                    # Cancel any running thinking task when a new event arrives
                    if current_thinking_task and not current_thinking_task.done():
                        log(f"Cancelling thinking task due to '{event}' event")
                        current_thinking_task.cancel()
                        current_thinking_task = None

                    # Cancel any running listening task when a new event arrives
                    if current_listening_task and not current_listening_task.done():
                        log(f"Cancelling listening task due to '{event}' event")
                        current_listening_task.cancel()
                        current_listening_task = None

                    # Handle events
                    if event == "wake_word_detected":
                        log("→ Executing wake_word_detected()")
                        await iwake_word_detected()
                    elif event == "listening":
                        log("→ Starting listening task")
                        current_listening_task = asyncio.create_task(listening())
                    elif event == "tts_speaking":
                        log("→ Executing tts_speaking()")
                        await tts_speaking()
                    elif event == "tts_finished":
                        log("→ Executing tts_finished()")
                        await tts_finished()
                    elif event == "thinking":
                        log("→ Starting thinking task")
                        current_thinking_task = asyncio.create_task(thinking())
                    elif event == "idle":
                        log("→ Executing idle()")
                        await idle()
                    elif event in ["stt_text", "tts_text", "snapshot"]:
                        # These are informational events, just log them
                        pass
                    else:
                        log(f"⚠ Unknown event: {event}")

        except ConnectionRefusedError:
            log("❌ Error: Could not connect to websocket server at ws://localhost:6055")
        except Exception as e:
            log(f"❌ Error: {e}")
        finally:
            log("Shutting down motor control system...")
        log(f"Sleeping for {sleep_time} seconds before trying again...")
        time.sleep(sleep_time)
        sleep_time = sleep_time + 1


async def iwake_word_detected():
    """Pulse head forward, pulse mouth open"""
    log("  → Pulsing head forward...")
    motor_on(500, "head", 1)
    await asyncio.sleep(0.1)
    log("  → Pulsing mouth open...")
    motor_on(300, "mouth", 1)
    log("  ✓ wake_word_detected complete")


async def listening():
    """Continuously flap tail until cancelled"""
    log("  → Starting continuous tail flapping...")
    motor_on(300, "mouth", -1)
    
    # Tail flap while listening:
    # try:
    #     while True:
    #         motor_on(200, "tail", 1)
    #         await asyncio.sleep(0.250)
    #         motor_on(200, "tail", -1)
    #         await asyncio.sleep(0.500)
    # except asyncio.CancelledError:
    #     # Task was cancelled (new event received)
    #     motor_stop("tail")
    #     log("  ⚠ Listening interrupted by new event")
    #     raise


async def thinking():
    """Continuously pulse tail until cancelled or timeout reached"""
    timeout_seconds = 5.0
    start_time = time.time()
    pulse_count = 0

    log(f"  → Starting thinking loop (timeout: {timeout_seconds}s)")

    try:
        while (time.time() - start_time) < timeout_seconds:
            motor_on(300, "tail", 1)
            await asyncio.sleep(0.150)
            motor_on(300, "tail", -1)
            await asyncio.sleep(0.500)
            pulse_count += 1

        log(f"  ✓ thinking complete ({pulse_count} pulses)")
    except asyncio.CancelledError:
        # Task was cancelled (new event received)
        motor_stop("tail")
        log(f"  ⚠ Thinking interrupted after {pulse_count} pulses")
        raise


async def tts_speaking():
    """Pulse mouth open"""
    log("  → Pulsing mouth open...")
    motor_on(300, "mouth", 1)
    log("  ✓ tts_speaking complete")


async def tts_finished():
    """Close mouth and retract head"""
    log("  → Closing mouth...")
    motor_on(300, "mouth", -1)
    await asyncio.sleep(1.0)
    log("  → Retracting head...")
    motor_on(500, "head", -1)
    log("  ✓ tts_finished complete")


async def idle():
    """Return all motors to neutral position"""
    log("  → Returning all motors to neutral...")
    for x in ["mouth", "head", "tail"]:
        motor_on(500, x, -1)
    await asyncio.sleep(1)

    log("  → Stopping all motors...")
    # Just to make sure it's off
    for x in ["mouth", "head", "tail"]:
        motor_stop(x)
    log("  ✓ idle complete")


if __name__ == "__main__":
    asyncio.run(main())