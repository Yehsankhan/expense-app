import matplotlib.pyplot as plt

def show_pie_chart(data):
    if not data:
        print("No data")
        return

    labels = [i[0] for i in data]
    values = [i[1] for i in data]

    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("Expense Breakdown")
    plt.show()
