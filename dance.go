package main

import (
	"fmt"
	"io/ioutil"
	"math"
	"os"
	"strconv"
	"strings"
	"time"
)

type Node struct {
	key                           int
	size                          int
	left, right, up, down, column *Node
}

type DancingLinks struct {
	head                        *Node
	columns                     []*Node
	use_greedy_column_selection bool
	solution                    []int
	all_solutions               [][]int
	nodes_searched              int
}

func SingletonNode() *Node {
	node := &Node{key: 0, size: 0}
	node.left = node
	node.right = node
	node.up = node
	node.down = node
	return node
}

func BuildDancingLinks(matrix [][]bool) *DancingLinks {
	n_columns := len(matrix[0])

	dl := &DancingLinks{}
	dl.head = SingletonNode()
	dl.BuildEmptyColumns(n_columns)
	for i, row := range matrix {
		dl.InsertRow(row, i)
	}
	return dl
}

func (dl *DancingLinks) BuildEmptyColumns(n_columns int) {
	dl.columns = make([]*Node, n_columns)

	if n_columns <= 0 {
		return
	}

	current := dl.head
	for i := range dl.columns {
		dl.columns[i] = SingletonNode()
		dl.columns[i].size = 0
		dl.columns[i].key = i

		next := dl.columns[i]
		current.right = next
		next.left = current
		current = next
	}

	current.right = dl.head
	dl.head.left = current
}

func (dl *DancingLinks) InsertSingleElement(column *Node, key int) *Node {
	node := &Node{key: key}

	column.size += 1
	node.column = column
	node.down = column
	node.up = column.up
	column.up.down = node
	column.up = node

	return node
}

func (dl *DancingLinks) InsertRow(row []bool, key int) {
	var current, first *Node

	for i, v := range row {
		if v {
			node := dl.InsertSingleElement(dl.columns[i], key)

			if current != nil {
				current.right = node
				node.left = current
			} else {
				first = node
			}

			current = node
		}
	}

	if current != nil {
		current.right = first
		first.left = current
	}
}

func (dl *DancingLinks) Cover(column *Node) {
	column.right.left = column.left
	column.left.right = column.right

	for i := column.down; i != column; i = i.down {
		for j := i.right; j != i; j = j.right {
			j.down.up = j.up
			j.up.down = j.down
			j.column.size -= 1
		}
	}
}

func (dl *DancingLinks) Uncover(column *Node) {
	for i := column.up; i != column; i = i.up {
		for j := i.left; j != i; j = j.left {
			j.column.size += 1
			j.down.up = j
			j.up.down = j
		}
	}

	column.right.left = column
	column.left.right = column
}

func (dl *DancingLinks) SelectColumn() *Node {
	if !dl.use_greedy_column_selection {
		return dl.head.right
	}

	best_size := math.MaxInt32
	best_c := (*Node)(nil)

	for c := dl.head.right; c != dl.head; c = c.right {
		if c.size < best_size {
			best_size = c.size
			best_c = c
		}
	}

	return best_c
}

func (dl *DancingLinks) Search() {
	if dl.head.right == dl.head {
		dl.all_solutions = append(dl.all_solutions, append([]int{}, dl.solution...))
		return
	}

	c := dl.SelectColumn()
	dl.nodes_searched += 1

	dl.Cover(c)
	for r := c.down; r != c; r = r.down {
		dl.solution = append(dl.solution, r.key)
		for j := r.right; j != r; j = j.right {
			dl.Cover(j.column)
		}
		dl.Search()
		for j := r.left; j != r; j = j.left {
			dl.Uncover(j.column)
		}
		dl.solution = dl.solution[:len(dl.solution)-1]
	}
	dl.Uncover(c)
}

func (dl *DancingLinks) AllSolutions() [][]int {
	dl.solution = make([]int, 0)
	dl.all_solutions = make([][]int, 0)
	dl.nodes_searched = 0

	start := time.Now()
	dl.Search()
	elapsed := time.Since(start).Seconds()

	fmt.Printf("Nodes searched: %d\n", dl.nodes_searched)
	fmt.Printf("Solutions found: %d\n", len(dl.all_solutions))
	fmt.Printf("Time elapsed: %f\n", elapsed)
	return dl.all_solutions
}

func LoadProblem(filename string) [][]bool {
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	lines := strings.Split(string(data), "\n")
	matrix := make([][]bool, len(lines))

	for i, line := range lines {
		values := strings.Split(line, " ")
		matrix[i] = make([]bool, len(values))

		for j, v := range values {
			matrix[i][j], _ = strconv.ParseBool(v)
		}
	}

	return matrix
}

func SaveSolution(filename string, solution [][]int) {
	lines := make([]string, 0, len(solution))
	for _, s := range solution {
		strs := make([]string, 0, len(s))
		for _, v := range s {
			strs = append(strs, strconv.Itoa(v))
		}

		lines = append(lines, strings.Join(strs, " "))
	}
	lines = append(lines, "")
	data := []byte(strings.Join(lines, "\n"))

	err := ioutil.WriteFile(filename, data, 0664)
	if err != nil {
		panic(err)
	}
}

func main() {
	if len(os.Args) < 3 {
		fmt.Printf("Usage: %s <problem input> <solution output>\n", os.Args[0])
		os.Exit(1)
	}

	matrix := LoadProblem(os.Args[1])
	dl := BuildDancingLinks(matrix)
	dl.use_greedy_column_selection = true

	solutions := dl.AllSolutions()

	SaveSolution(os.Args[2], solutions)
}
