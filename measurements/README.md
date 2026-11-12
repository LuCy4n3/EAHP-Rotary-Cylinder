# New hardware measurements

Run the serial acquisition utility from this directory so new output is separate
from the curated datasets in `data/`:

```powershell
..\.venv\Scripts\python.exe ..\tools\finalCode.py
```

Review the serial port, voltage conversion and connected firmware first. The
utility sends actuator/output commands. Its generated capture folders and counter
files are local and ignored by Git.
