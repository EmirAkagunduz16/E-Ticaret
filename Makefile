.PHONY: setup install test test-unit test-integration test-selenium test-performance test-api run clean help

# Varsayılan hedef
.DEFAULT_GOAL := help

# Renk tanımları
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m # No Color

# Proje kurulumu
setup: ## Projeyi kurar (venv oluşturur ve bağımlılıkları yükler)
	@echo "${GREEN}Sanal ortam oluşturuluyor...${NC}"
	python3 -m venv venv
	@echo "${GREEN}Gereksinimler yükleniyor...${NC}"
	. venv/bin/activate && pip install -r requirements.txt && pip install -r test-requirements.txt
	@echo "${GREEN}Kurulum tamamlandı!${NC}"

install: ## Sadece bağımlılıkları yükler
	@echo "${GREEN}Gereksinimler yükleniyor...${NC}"
	pip install -r requirements.txt
	pip install -r test-requirements.txt

# Veritabanı işlemleri
init-db: ## Veritabanını başlatır
	@echo "${GREEN}Veritabanı başlatılıyor...${NC}"
	. venv/bin/activate && python init_db.py

update-db: ## Veritabanını günceller
	@echo "${GREEN}Veritabanı güncelleniyor...${NC}"
	. venv/bin/activate && python update_db.py

# Test işlemleri
test: ## Tüm testleri çalıştırır
	@echo "${GREEN}Tüm testler çalıştırılıyor...${NC}"
	. venv/bin/activate && python run_tests.py --all

test-unit: ## Sadece unit testleri çalıştırır
	@echo "${GREEN}Unit testler çalıştırılıyor...${NC}"
	. venv/bin/activate && python run_tests.py --unit

test-integration: ## Sadece entegrasyon testlerini çalıştırır
	@echo "${GREEN}Entegrasyon testleri çalıştırılıyor...${NC}"
	. venv/bin/activate && python run_tests.py --integration

test-selenium: ## Sadece Selenium UI testlerini çalıştırır
	@echo "${GREEN}Selenium UI testleri çalıştırılıyor...${NC}"
	. venv/bin/activate && python run_tests.py --selenium

test-performance: ## Performans testlerini çalıştırır
	@echo "${GREEN}Performans testleri çalıştırılıyor...${NC}"
	. venv/bin/activate && python run_tests.py --performance

# Uygulama çalıştırma
run: ## Uygulamayı çalıştırır
	@echo "${GREEN}Uygulama başlatılıyor...${NC}"
	. venv/bin/activate && python app.py

run-prod: ## Uygulamayı production modunda çalıştırır
	@echo "${GREEN}Uygulama production modunda başlatılıyor...${NC}"
	. venv/bin/activate && FLASK_ENV=production python -m flask run --host=0.0.0.0

# Temizlik işlemleri
clean: ## Geçici dosyaları ve önbelleği temizler
	@echo "${GREEN}Geçici dosyalar temizleniyor...${NC}"
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.log" -delete

# Yardım
help: ## Bu yardım mesajını gösterir
	@echo "${YELLOW}Kullanılabilir komutlar:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "${YELLOW}Örnek kullanım:${NC}"
	@echo "  make setup     # Projeyi kurar"
	@echo "  make test      # Tüm testleri çalıştırır"
	@echo "  make run       # Uygulamayı çalıştırır" 