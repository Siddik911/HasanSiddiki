"""
Windows Pomodoro Timer
A simple background Pomodoro timer with native Windows notifications.
"""

import time
import sys

try:
    from win10toast import ToastNotifier
except ImportError:
    print("Error: win10toast is required. Install it with: pip install win10toast")
    sys.exit(1)


def notify(title: str, message: str, duration: int = 5) -> None:
    """Display a Windows toast notification."""
    toaster = ToastNotifier()
    toaster.show_toast(
        title,
        message,
        duration=duration,
        threaded=True
    )
    # Small delay to ensure notification displays
    time.sleep(0.5)


def run_pomodoro(focus_time: int = 3, break_time: int = 1, number_of_cycles: int = 100000000) -> None:
    """
    Run the Pomodoro timer.
    
    Args:
        focus_time: Duration of focus sessions in minutes (default: 25)
        break_time: Duration of break sessions in minutes (default: 5)
        number_of_cycles: Number of focus/break cycles to complete (default: 4)
    """
    print(f"🍅 Pomodoro Timer Started")
    print(f"   Focus time: {focus_time} minutes")
    print(f"   Break time: {break_time} minutes")
    print(f"   Cycles: {number_of_cycles}")
    print(f"   Press Ctrl+C to stop\n")
    
    focus_seconds = focus_time * 60
    break_seconds = break_time * 60
    
    for cycle in range(1, number_of_cycles + 1):
        # Focus session
        print(f"[Cycle {cycle}/{number_of_cycles}] 🎯 Focus session started...")
        notify(
            "🍅 Pomodoro - Focus Time",
            f"Cycle {cycle}/{number_of_cycles}: Time to focus for {focus_time} minutes!"
        )
        time.sleep(focus_seconds)
        
        # Break session (skip break after last cycle)
        if cycle < number_of_cycles:
            print(f"[Cycle {cycle}/{number_of_cycles}] ☕ Break time!")
            notify(
                "🍅 Pomodoro - Break Time",
                f"Cycle {cycle}/{number_of_cycles} complete! Take a {break_time} minute break."
            )
            time.sleep(break_seconds)
        else:
            print(f"[Cycle {cycle}/{number_of_cycles}] ✅ Final cycle complete!")
    
    # All cycles completed
    print("\n🎉 All Pomodoro cycles completed!")
    notify(
        "🍅 Pomodoro - Complete!",
        f"Congratulations! You completed {number_of_cycles} focus cycles.",
        duration=10
    )


def get_user_config() -> tuple[int, int, int]:
    """Get timer configuration from user input."""
    print("=" * 40)
    print("       🍅 POMODORO TIMER SETUP 🍅")
    print("=" * 40)
    print("Press Enter to use default values.\n")
    
    # Focus time
    focus_input = input("Focus time in minutes [25]: ").strip()
    focus_time = int(focus_input) if focus_input else 25
    
    # Break time
    break_input = input("Break time in minutes [5]: ").strip()
    break_time = int(break_input) if break_input else 5
    
    # Number of cycles
    cycles_input = input("Number of cycles [4]: ").strip()
    number_of_cycles = int(cycles_input) if cycles_input else 4
    
    print()
    return focus_time, break_time, number_of_cycles


def main() -> None:
    """Main entry point for the Pomodoro timer."""
    try:
        focus_time, break_time, number_of_cycles = get_user_config()
        
        # Validate inputs
        if focus_time <= 0 or break_time <= 0 or number_of_cycles <= 0:
            print("Error: All values must be positive integers.")
            sys.exit(1)
        
        run_pomodoro(focus_time, break_time, number_of_cycles)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Pomodoro timer stopped by user.")
        notify("🍅 Pomodoro - Stopped", "Timer was stopped by user.")
        sys.exit(0)
    except ValueError:
        print("Error: Please enter valid numbers.")
        sys.exit(1)


if __name__ == "__main__":
    main()
