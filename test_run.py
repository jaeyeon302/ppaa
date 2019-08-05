#!/usr/bin/env python3
import ppaa

app = ppaa.create_app()
if __name__ == "__main__":
	app.run(host='0.0.0.0',port=8080)
