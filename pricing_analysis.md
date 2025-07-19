# Análise de Custos e Precificação

## Custos das APIs (Pay-per-use)

### Fal.ai
- **FLUX Schnell**: $0.003/megapixel (~$0.003 por imagem 1MP)
- **FLUX Dev**: $0.025/megapixel (~$0.025 por imagem 1MP)
- **FLUX Pro**: $0.05/megapixel (~$0.05 por imagem 1MP)
- **Vídeo (Luma)**: $0.5 por vídeo
- **Vídeo (Kling)**: $0.095 por segundo

### Replicate
- **FLUX Dev**: ~$0.025 por imagem
- **FLUX Schnell**: ~$0.003 por imagem
- **Vídeo (MiniMax)**: ~$0.5 por vídeo
- **Música (Suno)**: ~$0.02 por segundo

### OpenAI (quando implementado)
- **GPT-4o**: $0.0025/1K tokens input, $0.01/1K tokens output
- **GPT-4**: $0.03/1K tokens input, $0.06/1K tokens output
- **DALL-E 3**: $0.04 por imagem (1024x1024)

### Anthropic Claude (quando implementado)
- **Claude 3.5 Sonnet**: $0.003/1K tokens input, $0.015/1K tokens output

## Cálculo de Custos por Plano

### Plano Mini ($3.80/mês)
**Recursos:**
- 100 mensagens GPT-4o/dia (3.000/mês)
- 10 imagens/mês
- 5 músicas/mês

**Custos estimados:**
- GPT-4o: 3.000 msgs × 150 tokens avg × $0.0025/1K = $1.125
- Imagens: 10 × $0.025 = $0.25
- Músicas: 5 × 30s × $0.02 = $3.00
- **Total de custos: $4.375**
- **Receita: $3.80**
- **Margem: -$0.575 (PREJUÍZO)**

### Plano Starter ($7.97/mês)
**Recursos:**
- 25 mensagens GPT-4/dia (750/mês)
- 30 imagens/mês
- 10 músicas/mês

**Custos estimados:**
- GPT-4: 750 msgs × 150 tokens avg × $0.03/1K = $3.375
- Imagens: 30 × $0.025 = $0.75
- Músicas: 10 × 30s × $0.02 = $6.00
- **Total de custos: $10.125**
- **Receita: $7.97**
- **Margem: -$2.155 (PREJUÍZO)**

### Plano Premium ($12.97/mês)
**Recursos:**
- 50 mensagens GPT-4/dia (1.500/mês)
- 100 imagens/mês
- 20 músicas/mês

**Custos estimados:**
- GPT-4: 1.500 msgs × 150 tokens avg × $0.03/1K = $6.75
- Imagens: 100 × $0.025 = $2.50
- Músicas: 20 × 30s × $0.02 = $12.00
- **Total de custos: $21.25**
- **Receita: $12.97**
- **Margem: -$8.28 (PREJUÍZO ALTO)**

## 🚨 PROBLEMA IDENTIFICADO

Os preços atuais estão muito baixos! Todos os planos geram prejuízo.

## Sugestão de Novos Preços (Margem 40-60%)

### Plano Mini - $9.99/mês
**Recursos ajustados:**
- 50 mensagens GPT-4o/dia (1.500/mês)
- 15 imagens/mês (FLUX Schnell)
- 3 músicas/mês

**Custos estimados:**
- GPT-4o: 1.500 × 100 tokens × $0.0025/1K = $0.375
- Imagens: 15 × $0.003 = $0.045
- Músicas: 3 × 30s × $0.02 = $1.80
- **Total de custos: $2.22**
- **Receita: $9.99**
- **Margem: $7.77 (78% lucro)**

### Plano Starter - $19.99/mês
**Recursos ajustados:**
- 100 mensagens GPT-4o/dia (3.000/mês)
- 50 imagens/mês (FLUX Dev)
- 10 músicas/mês
- 5 vídeos/mês

**Custos estimados:**
- GPT-4o: 3.000 × 100 tokens × $0.0025/1K = $0.75
- Imagens: 50 × $0.025 = $1.25
- Músicas: 10 × 30s × $0.02 = $6.00
- Vídeos: 5 × $0.5 = $2.50
- **Total de custos: $10.50**
- **Receita: $19.99**
- **Margem: $9.49 (47% lucro)**

### Plano Premium - $39.99/mês
**Recursos ajustados:**
- 200 mensagens GPT-4/dia (6.000/mês)
- 150 imagens/mês (FLUX Pro)
- 25 músicas/mês
- 15 vídeos/mês

**Custos estimados:**
- GPT-4: 6.000 × 100 tokens × $0.03/1K = $18.00
- Imagens: 150 × $0.05 = $7.50
- Músicas: 25 × 30s × $0.02 = $15.00
- Vídeos: 15 × $0.5 = $7.50
- **Total de custos: $48.00**
- **Receita: $39.99**
- **Margem: -$8.01 (AINDA PREJUÍZO)**

### Plano Premium Ajustado - $59.99/mês
**Recursos ajustados:**
- 100 mensagens GPT-4/dia (3.000/mês)
- 100 imagens/mês (FLUX Pro)
- 20 músicas/mês
- 10 vídeos/mês

**Custos estimados:**
- GPT-4: 3.000 × 100 tokens × $0.03/1K = $9.00
- Imagens: 100 × $0.05 = $5.00
- Músicas: 20 × 30s × $0.02 = $12.00
- Vídeos: 10 × $0.5 = $5.00
- **Total de custos: $31.00**
- **Receita: $59.99**
- **Margem: $28.99 (48% lucro)**

### Plano Ultimate - $99.99/mês
**Recursos:**
- 300 mensagens GPT-4/dia (9.000/mês)
- 300 imagens/mês (FLUX Pro)
- 50 músicas/mês
- 30 vídeos/mês
- Claude 3M tokens/mês

**Custos estimados:**
- GPT-4: 9.000 × 100 tokens × $0.03/1K = $27.00
- Imagens: 300 × $0.05 = $15.00
- Músicas: 50 × 30s × $0.02 = $30.00
- Vídeos: 30 × $0.5 = $15.00
- Claude: 3M tokens × $0.015/1K = $45.00
- **Total de custos: $132.00**
- **Receita: $99.99**
- **Margem: -$32.01 (PREJUÍZO)**

### Plano Ultimate Ajustado - $149.99/mês
**Recursos ajustados:**
- 200 mensagens GPT-4/dia (6.000/mês)
- 200 imagens/mês (FLUX Pro)
- 30 músicas/mês
- 20 vídeos/mês
- Claude 1M tokens/mês

**Custos estimados:**
- GPT-4: 6.000 × 100 tokens × $0.03/1K = $18.00
- Imagens: 200 × $0.05 = $10.00
- Músicas: 30 × 30s × $0.02 = $18.00
- Vídeos: 20 × $0.5 = $10.00
- Claude: 1M tokens × $0.015/1K = $15.00
- **Total de custos: $71.00**
- **Receita: $149.99**
- **Margem: $78.99 (53% lucro)**

## Recomendação Final

### Estrutura de Preços Sugerida:

1. **Free** - $0/mês
   - 5 mensagens GPT-4o/dia
   - 3 imagens/mês (FLUX Schnell)
   - 1 música/mês

2. **Starter** - $9.99/mês
   - 50 mensagens GPT-4o/dia
   - 15 imagens/mês (FLUX Schnell)
   - 3 músicas/mês

3. **Pro** - $19.99/mês
   - 100 mensagens GPT-4o/dia
   - 50 imagens/mês (FLUX Dev)
   - 10 músicas/mês
   - 5 vídeos/mês

4. **Premium** - $59.99/mês
   - 100 mensagens GPT-4/dia
   - 100 imagens/mês (FLUX Pro)
   - 20 músicas/mês
   - 10 vídeos/mês

5. **Ultimate** - $149.99/mês
   - 200 mensagens GPT-4/dia
   - 200 imagens/mês (FLUX Pro)
   - 30 músicas/mês
   - 20 vídeos/mês
   - Claude 1M tokens/mês

**Margem de lucro:** 45-55% em todos os planos
**Competitividade:** Preços justos comparados ao mercado

