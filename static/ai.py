print("🔥 Welcome to Smart Study Assistant 🔥")

name = input("Apna naam batao: ")
goal = input("Aaj kya padhna hai? ")
time = int(input("Kitne ghante padhoge? "))

print("\n📚 Study Plan for", name)

if time >= 3:
    print("🔥 Great! Tum serious ho")
    print("👉 2 hours:", goal)
    print("👉 1 hour: Revision")
elif time >= 1:
    print("👍 Good start")
    print("👉 45 min:", goal)
    print("👉 15 min: Revision")
else:
    print("⚠️ Time kam hai, focus karo")
    print("👉 Bas 30 min deep focus")

print("\n💬 Motivation:")
print("“Consistency hi real power hai”")