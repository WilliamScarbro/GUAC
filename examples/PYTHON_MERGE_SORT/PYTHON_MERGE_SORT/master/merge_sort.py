import sys

def merge_sort(array, left_index, right_index, comparison_function):
    if left_index >= right_index:
        return

    middle = (left_index + right_index)//2
    merge_sort(array, left_index, middle, comparison_function)
    merge_sort(array, middle + 1, right_index, comparison_function)
    merge(array, left_index, right_index, middle, comparison_function)

def merge(array, left_index, right_index, middle, comparison_function):
    left_array = array[left_index:middle+1]
    right_array = array[middle+1:right_index+1]

    i = j = 0
    k = left_index

    while i < len(left_array) and j < len(right_array):
        if comparison_function(left_array[i], right_array[j]):
            array[k] = left_array[i]
            i += 1
        else:
            array[k] = right_array[j]
            j += 1
        k += 1

    while i < len(left_array):
        array[k] = left_array[i]
        i += 1
        k += 1

    while j < len(right_array):
        array[k] = right_array[j]
        j += 1
        k += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python merge_sort_interface.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]

    try:
        with open(file_name, 'r') as file:
            numbers = [int(line) for line in file]

        merge_sort(numbers, 0, len(numbers) - 1, lambda a, b: a < b)

        print("Sorted numbers:")
        for number in numbers:
            print(number)

    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
    except ValueError:
        print(f"Invalid data in file '{file_name}'. Expected integers.")
