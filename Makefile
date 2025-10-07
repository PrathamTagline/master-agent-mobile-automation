.PHONY: help list list-all run run-all run-pc1 run-pc2 run-pc3 distribution agent master

help:
	@echo "Multi-PC Device Manager Commands"
	@echo ""
	@echo "Listing Devices:"
	@echo "  make list-all          - List all devices from all PCs"
	@echo "  make list PC=PC1       - List devices from specific PC"
	@echo ""
	@echo "Running Automation:"
	@echo "  make run-all           - Run on all devices (distributed apps)"
	@echo "  make run-all APP=nail_app  - Run specific app on all devices"
	@echo "  make run-pc1           - Run on PC1 devices only"
	@echo "  make run-pc2 APP=birthday_app  - Run app on PC2 devices"
	@echo ""
	@echo "Configuration:"
	@echo "  make distribution      - Show app distribution config"
	@echo ""
	@echo "Server Management:"
	@echo "  make agent             - Start agent server (run on each PC)"
	@echo "  make master            - Start master controller"

# List all devices
list-all:
	cd master && python3 master.py list-all

# List devices from specific PC
list:
ifndef PC
	@echo "Usage: make list PC=PC1"
	@exit 1
endif
	cd master && python3 master.py list --pc $(PC)

# Run on all devices with distribution
run-all:
ifdef APP
	cd master && python3 master.py run-all --app $(APP)
else
	cd master && python3 master.py run-all
endif

# Run on PC1
run-pc1:
ifdef APP
	cd master && python3 master.py run-pc --pc PC1 --app $(APP)
else
	cd master && python3 master.py run-pc --pc PC1
endif

# Run on PC2
run-pc2:
ifdef APP
	cd master && python3 master.py run-pc --pc PC2 --app $(APP)
else
	cd master && python3 master.py run-pc --pc PC2
endif

# Run on PC3
run-pc3:
ifdef APP
	cd master && python3 master.py run-pc --pc PC3 --app $(APP)
else
	cd master && python3 master.py run-pc --pc PC3
endif

# Show distribution
distribution:
	cd master && python3 master.py distribution

# Start agent server (run on each PC)
agent:
	cd agents && python3 agent.py

# Start master controller
master:
	@echo "Use specific commands like 'make run-all' instead"