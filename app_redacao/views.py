import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline

try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    print("Pipeline de análise de sentimento Transformer carregado com sucesso.")
except Exception as e:
    sentiment_analyzer = None
    print(f"Erro ao carregar o pipeline de análise de sentimento: {e}")
    print("Certifique-se de ter 'torch' ou 'tensorflow' instalados e conexão com a internet para baixar o modelo.")


@csrf_exempt 
def corrigir_redacao(request):
    if request.method == 'POST':
        texto_redacao = request.POST.get('essay_content', '')

        if not texto_redacao:
            return JsonResponse({'error': 'Nenhum conteúdo de redação fornecido.'}, status=400)

        if sentiment_analyzer is None:
            return JsonResponse({'error': 'O pipeline de IA não foi carregado. Verifique os logs do servidor.'}, status=500)

        nota_prevista = 0
        pontos_fortes = []
        pontos_fracos = []

        try:
    
            sentiment_result = sentiment_analyzer(texto_redacao)
            print(f"Resultado bruto do sentimento: {sentiment_result}")

            if sentiment_result and len(sentiment_result) > 0:
                label = sentiment_result[0]['label']
                score_confianca = sentiment_result[0]['score']

                if '1 star' in label:
                    nota_prevista = int(score_confianca * 200) 
                    pontos_fracos.append("O texto pode ter um tom negativo ou expressar pessimismo.")
                    pontos_fracos.append("A clareza e o desenvolvimento das ideias podem ser melhorados.")
                    pontos_fortes.append("Identificação de um tom expressivo.")
                elif '2 stars' in label:
                    nota_prevista = int(250 + score_confianca * 250)
                    pontos_fracos.append("O texto tem um tom ligeiramente negativo ou expressa pouca clareza.")
                    pontos_fracos.append("Argumentos podem ser mais bem elaborados.")
                    pontos_fortes.append("Demonstra alguma tentativa de argumentação.")
                elif '3 stars' in label:
                    nota_prevista = int(500 + score_confianca * 250)
                    pontos_fortes.append("O texto apresenta um tom neutro e equilibrado.")
                    pontos_fracos.append("Pode faltar um posicionamento mais claro ou aprofundamento das ideias.")
                    pontos_fortes.append("Coerência textual básica presente.")
                elif '4 stars' in label:
                    nota_prevista = int(750 + score_confianca * 200)
                    pontos_fortes.append("O texto exibe um tom predominantemente positivo e bem desenvolvido.")
                    pontos_fortes.append("Argumentação clara e organizada.")
                    pontos_fracos.append("Possíveis melhorias em detalhes ou na proposta de intervenção.")
                elif '5 stars' in label:
                    nota_prevista = 1000 
                    pontos_fortes.append("O texto demonstra um tom muito positivo e uma argumentação robusta.")
                    pontos_fortes.append("Excelente desenvolvimento de ideias e clareza expositiva.")
                    pontos_fortes.append("Concisão e impacto na mensagem.")
                else:
                    nota_prevista = 0 
                    pontos_fracos.append("Não foi possível determinar o sentimento principal do texto.")
                    pontos_fracos.append("Verifique se o texto é muito curto ou ambíguo.")

               
                nota_prevista = max(0, min(1000, nota_prevista))

            else:
                nota_prevista = 0
                pontos_fracos.append("Não foi possível analisar o sentimento da redação.")

        except Exception as e:
            print(f"Erro durante a análise da redação com o pipeline Transformer: {e}")
            return JsonResponse({'error': f'Ocorreu um erro durante o processamento da redação: {e}'}, status=500)

        # Preparar a resposta
        response_data = {
            'score': nota_prevista,
            'strengths': pontos_fortes,
            'weaknesses': pontos_fracos,
            'received_text': texto_redacao
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Apenas requisições POST são permitidas.'}, status=405)

def formulario_redacao_view(request):
    return render(request, 'app_redacao/formulario_redacao.html')
