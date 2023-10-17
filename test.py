def pad_matrix_with_edge_values(matrix):
    if not matrix:
        return matrix

    top_padding = matrix[0]
    bottom_padding = matrix[-1]
    top_bottom_padded_matrix = []
    
    top_bottom_padded_matrix.append(top_padding)
    for row in matrix:
        top_bottom_padded_matrix.append(row)
    top_bottom_padded_matrix.append(bottom_padding)
    
        
    resulting_matrix = []
    
    for row in top_bottom_padded_matrix:
        side_padded_row = [row[0]] + row + [row[-1]]
        resulting_matrix.append(side_padded_row)
        
    print(resulting_matrix)
    
# Example usage:
original_matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

padded_matrix = pad_matrix_with_edge_values(original_matrix)
