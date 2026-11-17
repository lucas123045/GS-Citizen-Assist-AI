# Citizen Assist AI - Módulo de decisão lógica

Global Solution GS26_2 - Computer Science - 1CC

Integrantes:

- Lucas Klein da Veiga - RM570029
- Alexandre Rizzi de Mattos - RM569621
- Miguel Putini - RM571624

## Tema

Orientação sobre a isenção da taxa de inscrição do Enem, com base no item 2.3 do Edital Inep nº 21/2026.

| Variável | 1 | 0 |
| --- | --- | --- |
| A | está na última série do ensino médio em escola pública | não está |
| B | fez todo o ensino médio em escola pública ou com bolsa integral | não fez |
| C | renda familiar per capita de até 1,5 salário mínimo | renda maior |
| D | família de baixa renda inscrita no CadÚnico | não inscrita |
| S | perfil compatível com a isenção | não compatível |

Forma canônica: `S = ΠM(0,2,4) = (A+B+C+D)(A+B+C'+D)(A+B'+C+D)`

Forma simplificada: `S = A + B·C + D`

## Como rodar

Precisa de Python 3.8 ou mais novo. Não usa bibliotecas externas.

```bash
python -m citizen_assist
python -m citizen_assist --entradas 0110
python -m citizen_assist --tabela
python -m unittest -v
```

O primeiro comando faz as perguntas. O segundo recebe A B C D direto. O terceiro testa as 16 combinações e o último roda os testes.

Simulador: abrir `simulador/index.html` no navegador.

Relatório: `relatorio/Relatorio_Tecnico_GS26_2_CitizenAssist.pdf`

## Pastas

- `citizen_assist/` - lógica e programa
- `tests/` - testes
- `simulador/` - simulador no navegador
- `relatorio/` - relatório em PDF e prints

## Aviso

Protótipo acadêmico. Não é canal oficial do Inep/MEC e não confirma a concessão de isenção. O programa não pede dados pessoais e não grava respostas.
