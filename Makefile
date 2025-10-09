.PHONY: help list list-all run run-all run-pc run-device stop stop-all stop-pc stop-device logs logs-all logs-pc logs-device sessions sessions-all sessions-pc sessions-device distribution agent

help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Multi-PC Device Manager - Command Reference"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📱 LISTING DEVICES:"
	@echo "  make list-all              List all devices from all PCs"
	@echo "  make list PC=PC1           List devices from specific PC"
	@echo ""
	@echo "▶️  RUNNING AUTOMATION:"
	@echo "  make run-all               Run on all devices (distributed)"
	@echo "  make run-all APP=nail_app  Run specific app on all devices"
	@echo "  make run-pc PC=PC1         Run on PC1 devices only"
	@echo "  make run-pc PC=PC2 APP=birthday_app"
	@echo "  make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app"
	@echo ""
	@echo "⏹️  STOPPING AUTOMATION:"
	@echo "  make stop-all              Stop all devices on all PCs"
	@echo "  make stop-pc PC=PC1        Stop all devices on PC1"
	@echo "  make stop-device PC=PC1 DEVICE=emulator-5554"
	@echo ""
	@echo "📋 VIEWING LOGS:"
	@echo "  make logs-all              Show logs from all PCs"
	@echo "  make logs-all LINES=100    Show last 100 lines"
	@echo "  make logs-pc PC=PC1        Show logs from PC1"
	@echo "  make logs-device PC=PC1 DEVICE=emulator-5554"
	@echo ""
	@echo "📊 SESSION STATISTICS:"
	@echo "  make sessions-all          Show sessions from all devices"
	@echo "  make sessions-pc PC=PC1    Show sessions from PC1"
	@echo "  make sessions-device PC=PC1 DEVICE=emulator-5554"
	@echo ""
	@echo "⚙️  CONFIGURATION:"
	@echo "  make distribution          Show app distribution config"
	@echo ""
	@echo "🖥️  SERVER MANAGEMENT:"
	@echo "  make agent                 Start agent server (run on each PC)"
	@echo ""

# ============ LISTING ============

list-all:
	cd master && python3 master.py list-all

list:
ifndef PC
	@echo "❌ Usage: make list PC=PC1"
	@exit 1
endif
	cd master && python3 master.py list --pc $(PC)

# ============ RUNNING ============

run-all:
ifdef APP
	cd master && python3 master.py run-all --app $(APP)
else
	cd master && python3 master.py run-all
endif

run-pc:
ifndef PC
	@echo "❌ Usage: make run-pc PC=PC1 [APP=nail_app]"
	@exit 1
endif
ifdef APP
	cd master && python3 master.py run-pc --pc $(PC) --app $(APP)
else
	cd master && python3 master.py run-pc --pc $(PC)
endif

run-device:
ifndef PC
	@echo "❌ Usage: make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app"
	@exit 1
endif
ifndef DEVICE
	@echo "❌ DEVICE is required. Usage: make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app"
	@exit 1
endif
ifndef APP
	@echo "❌ APP is required. Usage: make run-device PC=PC1 DEVICE=emulator-5554 APP=nail_app"
	@exit 1
endif
	cd master && python3 master.py run-device --pc $(PC) --device $(DEVICE) --app $(APP)

# ============ STOPPING ============

stop-all:
	cd master && python3 master.py stop-all

stop-pc:
ifndef PC
	@echo "❌ Usage: make stop-pc PC=PC1"
	@exit 1
endif
	cd master && python3 master.py stop-pc --pc $(PC)

stop-device:
ifndef PC
	@echo "❌ Usage: make stop-device PC=PC1 DEVICE=emulator-5554"
	@exit 1
endif
ifndef DEVICE
	@echo "❌ DEVICE is required. Usage: make stop-device PC=PC1 DEVICE=emulator-5554"
	@exit 1
endif
	cd master && python3 master.py stop-device --pc $(PC) --device $(DEVICE)

# ============ LOGS ============

logs-all:
ifdef LINES
	cd master && python3 master.py logs-all --lines $(LINES)
else
	cd master && python3 master.py logs-all
endif

logs-pc:
ifndef PC
	@echo "❌ Usage: make logs-pc PC=PC1 [LINES=100]"
	@exit 1
endif
ifdef LINES
	cd master && python3 master.py logs-pc --pc $(PC) --lines $(LINES)
else
	cd master && python3 master.py logs-pc --pc $(PC)
endif

logs-device:
ifndef PC
	@echo "❌ Usage: make logs-device PC=PC1 DEVICE=emulator-5554 [LINES=100]"
	@exit 1
endif
ifndef DEVICE
	@echo "❌ DEVICE is required. Usage: make logs-device PC=PC1 DEVICE=emulator-5554"
	@exit 1
endif
ifdef LINES
	cd master && python3 master.py logs-device --pc $(PC) --device $(DEVICE) --lines $(LINES)
else
	cd master && python3 master.py logs-device --pc $(PC) --device $(DEVICE)
endif

# ============ SESSIONS ============

sessions-all:
	cd master && python3 master.py sessions-all

sessions-pc:
ifndef PC
	@echo "❌ Usage: make sessions-pc PC=PC1"
	@exit 1
endif
	cd master && python3 master.py sessions-pc --pc $(PC)

sessions-device:
ifndef PC
	@echo "❌ Usage: make sessions-device PC=PC1 DEVICE=emulator-5554"
	@exit 1
endif
ifndef DEVICE
	@echo "❌ DEVICE is required. Usage: make sessions-device PC=PC1 DEVICE=emulator-5554"
	@exit 1
endif
	cd master && python3 master.py sessions-device --pc $(PC) --device $(DEVICE)

# ============ CONFIGURATION ============

distribution:
	cd master && python3 master.py distribution

# ============ SERVER ============

agent:
	cd agents && python3 agent.py

# ============ SHORTCUTS ============

# Quick shortcuts for common operations
run-pc1:
ifdef APP
	$(MAKE) run-pc PC=PC1 APP=$(APP)
else
	$(MAKE) run-pc PC=PC1
endif

run-pc2:
ifdef APP
	$(MAKE) run-pc PC=PC2 APP=$(APP)
else
	$(MAKE) run-pc PC=PC2
endif

run-pc3:
ifdef APP
	$(MAKE) run-pc PC=PC3 APP=$(APP)
else
	$(MAKE) run-pc PC=PC3
endif

stop-pc1:
	$(MAKE) stop-pc PC=PC1

stop-pc2:
	$(MAKE) stop-pc PC=PC2

stop-pc3:
	$(MAKE) stop-pc PC=PC3

logs-pc1:
	$(MAKE) logs-pc PC=PC1

logs-pc2:
	$(MAKE) logs-pc PC=PC2

logs-pc3:
	$(MAKE) logs-pc PC=PC3

sessions-pc1:
	$(MAKE) sessions-pc PC=PC1

sessions-pc2:
	$(MAKE) sessions-pc PC=PC2

sessions-pc3:
	$(MAKE) sessions-pc PC=PC3