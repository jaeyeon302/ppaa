#!/usr/bin/env python3
import markit

app = markit.create_app()
if __name__ == "__main__":
	app.run(host='0.0.0.0',port=8080)
