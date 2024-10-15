from asyncio import run as asyncio_run
from src.dir_schedule.some_schedule import check_schedule


if __name__ == "__main__":
    asyncio_run(main=check_schedule(seconds=25))