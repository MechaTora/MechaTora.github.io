 #!/usr/bin/env python3
  import json
  import os

  print("Starting script...")

  try:
      os.makedirs('stock-monitor-pro/data', exist_ok=True)
      print("Directory created")

      data = {
          "success": True,
          "message": "Test successful",
          "data": [{"symbol": "TEST", "price": 100}]
      }

      with open('stock-monitor-pro/data/stocks.json', 'w') as f:
          json.dump(data, f)

      print("File written successfully")

  except Exception as e:
      print(f"Error: {e}")
      raise
