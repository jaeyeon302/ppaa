#!/usr/bin/env python3
import markit

if __name__ == "__main__":
	app = markit.create_app()
	app.run(host='0.0.0.0',port=8080)