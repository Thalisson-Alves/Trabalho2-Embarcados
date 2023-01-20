import os

SO_DIR = os.getenv(
    'SO_DIR', 
    os.path.join(
        os.path.dirname(__file__),
        '..', 'bin'
    )
)
