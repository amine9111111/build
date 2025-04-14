import os
import streamlit as st
import requests

# === Config ===
API_KEY = os.getenv("DEEPWOKEN_API_KEY")  # Récupérer la clé API depuis les secrets GitHub
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

# === Fonction de validation et correction des stats ===
def validate_and_correct_stats(str_, fort, agi, intel, will, cha, weapon, element, style):
    corrections = []
    corrected_stats = {
        'Strength': str_,
        'Fortitude': fort,
        'Agility': agi,
        'Intelligence': intel,
        'Willpower': will,
        'Charisma': cha
    }

    total = sum(corrected_stats.values())

    if total > 330:
        corrections.append(f"Le total des stats ({total}) dépasse la limite de 330. Des ajustements seront faits.")
        excess = total - 330

        # Réduction prioritaire des stats non essentielles
        for stat in ['Charisma', 'Intelligence', 'Willpower', 'Agility', 'Fortitude', 'Strength']:
            if excess <= 0:
                break
            if corrected_stats[stat] > 1:
                reducible = corrected_stats[stat] - 1
                reduction = min(reducible, excess)
                corrected_stats[stat] -= reduction
                excess -= reduction
                corrections.append(f"{reduction} points retirés de {stat}.")

    # Logique personnalisée par arme/style
    if weapon == "Greatsword" and corrected_stats['Strength'] < 80:
        corrections.append("Greatsword nécessite au moins 80 Strength. Ajustement effectué.")
        corrected_stats['Strength'] = 80

    if style == "Tank" and corrected_stats['Fortitude'] < 70:
        corrections.append("Tank nécessite au moins 70 Fortitude. Ajustement effectué.")
        corrected_stats['Fortitude'] = 70

    # Recalcul du total après corrections
    total = sum(corrected_stats.values())
    if total > 330:
        corrections.append(f"Le total corrigé est encore trop élevé ({total}). Réductions supplémentaires en cours...")
        excess = total - 330
        for stat in ['Charisma', 'Intelligence', 'Willpower', 'Agility']:
            if excess <= 0:
                break
            if corrected_stats[stat] > 20:
                reduction = min(corrected_stats[stat] - 20, excess)
                corrected_stats[stat] -= reduction
                excess -= reduction
                corrections.append(f"{reduction} points en moins sur {stat} pour rester dans la limite de 330.")

    return corrected_stats, corrections

# === UI Streamlit ===
st.title("🧠 Générateur de Build PVE - Deepwoken")

st.markdown("Remplis les infos ci-dessous et l'IA générera un build PVE 🔥")

race = st.selectbox("Race", [
    "Adret", "Ganymede", "Capra", "Khan", "Vesperian", "Lightborn",
    "Canor", "Felinor", "Etrean", "Gremor", "Chimeborn"
])
element = st.selectbox("Élément principal", [
    "Flamecharm", "Thundercall", "Galebreathe", "Frost", "Shadowcast", "Ironsing"
])
weapon = st.selectbox("Type d'arme", [
    "Épée", "Greatsword", "Gun", "Dagger", "Spear", "Fist", "Axe", "Rapier"
])
style = st.selectbox("Style de jeu", ["Tank", "Damage", "Mobility", "Support", "Mixte"])
level = st.slider("Niveau approximatif", 1, 20, 15)

# === Répartition manuelle des stats ===
st.markdown("### 🧮 Répartition des 330 points de stats")
str_ = st.number_input("Strength", 0, 330, 40)
fort = st.number_input("Fortitude", 0, 330, 40)
agi = st.number_input("Agility", 0, 330, 40)
intel = st.number_input("Intelligence", 0, 330, 40)
will = st.number_input("Willpower", 0, 330, 40)
cha = st.number_input("Charisma", 0, 330, 40)

total_points = str_ + fort + agi + intel + will + cha
st.markdown(f"**Total actuel :** {total_points} / 330")

submit = st.button("🛠️ Génère le build")

if submit:
    with st.spinner("L'IA réfléchit..."):

        # Validation et correction des stats
        corrected_stats, corrections = validate_and_correct_stats(str_, fort, agi, intel, will, cha, weapon, element, style)

        if corrections:
            st.markdown("### ⚠️ Corrections proposées :")
            for correction in corrections:
                st.markdown(f"- {correction}")

        # Mise à jour des stats avec les valeurs corrigées
        str_ = corrected_stats['Strength']
        fort = corrected_stats['Fortitude']
        agi = corrected_stats['Agility']
        intel = corrected_stats['Intelligence']
        will = corrected_stats['Willpower']
        cha = corrected_stats['Charisma']

        # Appel API IA
        messages = [
            {"role": "system", "content": "Tu es un expert en builds Deepwoken. Tu aides les joueurs à créer des builds PVE optimisés."},
            {"role": "user", "content": f"""
Je veux un build PVE pour Deepwoken avec ces infos :
- Race : {race}
- Élément : {element}
- Arme : {weapon}
- Style de jeu : {style}
- Niveau : {level}
- Stats : Strength {str_}, Fortitude {fort}, Agility {agi}, Intelligence {intel}, Willpower {will}, Charisma {cha}

Génère :
- La liste des talents clés (https://deepwoken.fandom.com/wiki/Talents)
- Les armes idéales
- Les armures conseillées
- Les mantras (sorts)
- Un résumé de gameplay
- Et pourquoi les choix sont bons pour le PVE

Réponds en français, de façon claire et structurée.
"""}
        ]

        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7
            }
        )

        if response.status_code == 200:
            build = response.json()["choices"][0]["message"]["content"]
            st.markdown("### 🔧 Build généré :")
            st.markdown(build)
        else:
            st.error("Erreur API : " + response.text)
