# Dockerfile durci multi-stage pour HILAI Studio
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Image finale allégée et sécurisée
FROM python:3.12-slim AS runner

WORKDIR /app

# Création d'un utilisateur non-root pour le principe du moindre privilège
RUN groupadd -g 1001 hilai && \
    useradd -u 1001 -g hilai -m -s /bin/bash hilaiuser

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copie des bibliothèques Python installées
COPY --from=builder /root/.local /home/hilaiuser/.local
ENV PATH=/home/hilaiuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copie des fichiers applicatifs
COPY --chown=hilaiuser:hilai . /app

# Création des dossiers de persistance avec les bons droits
RUN mkdir -p /app/sorties_a_valider /app/sauvegardes_studio && \
    chown -R hilaiuser:hilai /app

USER hilaiuser

# Point d'entrée en mode CLI (ou headless)
ENTRYPOINT ["python", "studio_lanceur.py", "--cli"]
