 #!/usr/bin/env python3
  import json
  import os

  print("Starting script...")

  try:
      print("Creating directory...")
      os.makedirs('stock-monitor-pro/data', exist_ok=True)
      print("Directory created successfully")

      print("Creating test data...")
      data = {
          "success": True,
          "message": "Test successful",
          "data": [{"symbol": "TEST", "price": 100}]
      }

      print("Writing file...")
      with open('stock-monitor-pro/data/stocks.json', 'w') as f:
          json.dump(data, f)

      print("File written successfully")
      print("Script completed without errors")

  except Exception as e:
      print(f"Error occurred: {e}")
      import traceback
      traceback.print_exc()
      exit(1)
