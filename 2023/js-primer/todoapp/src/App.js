import { TodoListModel } from "./model/TodoListModel.js";
import { TodoItemModel } from "./model/TodoItemModel.js";
import { TodoListView } from "./view/TodoListView.js";
import { render } from "./view/html-util.js";

export class App {
    #todoListView = new TodoListView();
    #todoListModel = new TodoListModel([]);

    formElement;
    formInputElement;
    todoCountElement;
    todoListContainerElement;
    constructor({ formElement, formInputElement, todoLisContainerElement, todoCountElement }) {
        this.formElement = formElement;
        this.formInputElement = formInputElement;
        this.todoCountElement = todoCountElement;
        this.todoListContainerElement = todoLisContainerElement;
    }

    /**
     * @param {string} title
     */
    #handleAdd = (title) => {
        this.#todoListModel.addTodo(new TodoItemModel({ title, completed: false }));
    };

    /**
     * @param {{ id: number, completed: boolean }}
     */
    #handleUpdate = ({ id, completed }) => {
        this.#todoListModel.updateTodo({ id, completed });
    };

    /**
     * @param {{ id: number }}
     */
    #handleDelete = ({ id }) => {
        this.#todoListModel.deleteTodo({ id });
    };

    /**
     * @param {Event} event
     */
    #handleSubmit = (event) => {
        event.preventDefault();
        const inputElement = this.formInputElement;
        this.#handleAdd(inputElement.value);
        inputElement.value = "";
    };

    #handleChange = () => {
        const todoCountElement = this.todoCountElement;
        const todoListContainerElement = this.todoListContainerElement;
        const todoItems = this.#todoListModel.getTodoItems();
        const todoListElement = this.#todoListView.createElement(todoItems, {
                onUpdateTodo: ({ id, completed }) => {
                    this.#handleUpdate({ id, completed });
                },
                onDeleteTodo: ({ id }) => {
                    this.#handleDelete({ id });
                }
        });

        render(todoListElement, todoListContainerElement);
        todoCountElement.textContent = `TodoItemCount: ${this.#todoListModel.getTotalCount()}`;
   };

    mount() {
        this.#todoListModel.onChange(this.#handleChange);
        this.formElement.addEventListener("submit", this.#handleSubmit);
    }

    unmount() {
        this.#todoListModel.offChange(this.#handleChange);
        this.formElement.removeEventListener("submit", this.#handleSubmit);
    }
}
