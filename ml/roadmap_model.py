import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# 🔹 Sample training data (simulated)
data = {
    "skill": ["Python", "Python", "SQL", "ML", "ML", "Pandas", "SQL", "Python"],
    "progress": [20, 60, 35, 80, 50, 40, 70, 90],
    "next_step": [
        "Revise Basics",
        "Practice Mini Projects",
        "Revise Basics",
        "Advanced Topics",
        "Practice Mini Projects",
        "Practice Mini Projects",
        "Advanced Topics",
        "Advanced Topics"
    ]
}

df = pd.DataFrame(data)

# 🔹 Encode categorical features
skill_encoder = LabelEncoder()
label_encoder = LabelEncoder()

df["skill_encoded"] = skill_encoder.fit_transform(df["skill"])
df["label"] = label_encoder.fit_transform(df["next_step"])

X = df[["skill_encoded", "progress"]]
y = df["label"]

# 🔹 Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 🔹 Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🔹 Save model & encoders
joblib.dump(model, "ml/roadmap_model.pkl")
joblib.dump(skill_encoder, "ml/skill_encoder.pkl")
joblib.dump(label_encoder, "ml/label_encoder.pkl")

print("✅ Roadmap ML model trained & saved")
