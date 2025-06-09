import csv

def analyze_stock_data(file_path):
    stock_statistics = []

    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Skip the header row

        for row in csv_reader:
            if not row or len(row) < 2:  # Skip empty or malformed rows
                continue

            company_name = row[0]
            try:
                daily_changes = list(map(float, row[1:]))
            except ValueError:
                continue  # Skip rows with non-numeric data

            # Calculate statistics
            overall_increase = sum(daily_changes)
            max_increase = max(daily_changes)
            max_decrease = min(daily_changes)
            average_change = overall_increase / len(daily_changes)

            stock_statistics.append({
                "CompanyName": company_name,
                "OverallIncrease": overall_increase,
                "MaxIncrease": max_increase,
                "MaxDecrease": max_decrease,
                "AverageChange": average_change
            })

    return stock_statistics


if __name__ == "__main__":
    file_path = "c:/Users/Administrator/Desktop/workingproj/neuedahackathon/sampledata.csv"
    stats = analyze_stock_data(file_path)

    for stat in stats:
        print(f"Company: {stat['CompanyName']}")
        print(f"  Overall Increase: {stat['OverallIncrease']:.2f}")
        print(f"  Max Increase: {stat['MaxIncrease']:.2f}")
        print(f"  Max Decrease: {stat['MaxDecrease']:.2f}")
        print(f"  Average Change: {stat['AverageChange']:.2f}")
        print()