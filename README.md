# Quiz Interactivo 🎓

App de opción múltiple con explicaciones, deployable en [Streamlit Community Cloud](https://streamlit.io/cloud).

## Estructura del proyecto

```
quiz-app/
├── app.py                  # Aplicación principal
├── requirements.txt        # Dependencias (solo streamlit)
├── README.md
└── data/
    └── questions.json      # ← Acá van todos tus temas y preguntas
```

## Cómo agregar un tema nuevo

Abrí `data/questions.json` y agregá un objeto al array `"topics"`:

```json
{
  "topics": [
    {
      "id": "mi-tema",              // identificador único (sin espacios)
      "title": "Nombre visible",    // lo que aparece en el menú
      "description": "Subtítulo opcional",
      "questions": [
        {
          "question": "Texto de la pregunta",
          "options": [
            "Opción A",
            "Opción B",
            "Opción C",
            "Opción D"
          ],
          "correct": 1,             // índice (0-3) de la opción correcta
          "explanation": "Por qué la opción B es correcta y las demás no..."
        }
      ]
    }
  ]
}
```

### Reglas del JSON
- `"correct"` es el **índice** de la opción correcta: `0` = A, `1` = B, `2` = C, `3` = D.
- Se soportan entre 2 y 5 opciones por pregunta.
- `"description"` es opcional.
- El JSON debe ser válido (podés verificarlo en [jsonlint.com](https://jsonlint.com)).

## Deploy en Streamlit Cloud

1. Subí este repositorio a GitHub.
2. Entrá a [share.streamlit.io](https://share.streamlit.io) y conectá tu cuenta de GitHub.
3. Elegí el repo, la branch y el archivo `app.py`.
4. Hacé clic en **Deploy** — listo.

Cada vez que hagas `git push` (por ejemplo para agregar preguntas), la app se actualiza automáticamente.

## Correr localmente

```bash
pip install streamlit
streamlit run app.py
```
