import asyncio
from motor_mgr import motor_on, motor_stop


async def test_motor(motor_name):
    """Test a single motor forward then backward"""
    print(f"\n{'='*50}")
    print(f"Testing motor: {motor_name}")
    print(f"{'='*50}")
    
    # Test forward
    print(f"→ {motor_name.upper()} moving FORWARD...")
    motor_on(1000, motor_name, 1)  # 1 second forward
    await asyncio.sleep(1.2)  # Wait for motor to finish
    
    # Brief pause between forward and backward
    await asyncio.sleep(0.5)
    
    # Test backward
    print(f"→ {motor_name.upper()} moving BACKWARD...")
    motor_on(1000, motor_name, -1)  # 1 second backward
    await asyncio.sleep(1.2)  # Wait for motor to finish
    
    print(f"✓ {motor_name.upper()} test complete\n")


async def main():
    """Test all motors"""
    print("╔════════════════════════════════════════╗")
    print("║     Motor Control System Test Suite    ║")
    print("╚════════════════════════════════════════╝\n")
    
    motors = ["head", "mouth", "tail"]
    
    try:
        for motor in motors:
            await test_motor(motor)
        
        print("\n╔════════════════════════════════════════╗")
        print("║        All tests completed! ✓         ║")
        print("╚════════════════════════════════════════╝")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
    finally:
        # Make sure all motors are stopped
        print("\nCleaning up... stopping all motors")
        for motor in motors:
            motor_stop(motor)
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
