import { EventEmitter } from "../EventEmitter.js";

export class TodoListModel extends EventEmitter {
    #items;

    /**
     * @param {TodoItemModel[]} [items] first item list
     */
    constructor(items = []){
        super();
        this.#items = items;
    }

    /**
     * @returns {number}
     */
    getTotalCount() {
        return this.#items.length;
    }

    /**
     * @returns {TodoItemModel[]}
     */
    getTodoItems() {
        return this.#items;
    }

    /**
     * @param {Function} listener
     */
    onChange(listener) {
        this.addEvenListener("change", listener);
    }

    /**
     * @param {Function} listener
     */
    offChange(listener) {
        this.removeEventListener("change", listener);
    }

    /**
     * call listener function
     */
    emitChange() {
        this.emit("change");
    }

    /**
     * @param {TodoItemModel} todoItem
     */
    addTodo(todoItem) {
        if (todoItem.isEmptyTitle()) {
            return;
        }
        this.#items.push(todoItem);
        this.emitChange();
    }
    
    /**
     * @param {{ id:numbner, completed: boolean }}
     */
    updateTodo({ id, completed }) {
        const todoItem = this.#items.find(todo => todo.id === id);
        if (!todoItem) {
            return;
        }
        todoItem.completed = completed;
        this.emitChange();
    }

    /**
     * @param {{ id: number }}
     */
    deleteTodo({ id }) {
        this.#items = this.#items.filter(todo => {
            return todo.id !== id;
        });
        this.emitChange();
    }
}
