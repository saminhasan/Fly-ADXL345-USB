# Fly-ADXL345-USB Accelerometer Reader

This project reads acceleration data from the Fly-ADXL345-USB over USB serial. It’s usually used with Klipper firmware for resonance compensation, but here it’s used as a standalone USB 3-axis accelerometer.
# Repo Contents

    RPI_PICO2-20250415-v1.25.0.uf2 – MicroPython firmware for the Pico

    flash_nuke.uf2 – Wipes the Pico flash

    main.py – Runs on Pico, talks to ADXL345 over SPI and streams data over USB

    getter.py – Host-side script to read and print data with timestamps
