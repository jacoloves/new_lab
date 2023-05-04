let todoIdx = 0;

export class TodoItemModel {
    /** @type {number} Todo item id */
    id;
    /** @type {string} Todo item title */
    title;
    /** @type {boolean} Todo item true or false */
    completed;

    /**
     * @param {{ title: string, completed: boolean }}
     */
    constructor ({ title, completed }) {
        this.id = todoIdx++;
        this.title = title;
        this.completed = completed;
    }

    /**
     * @returns {boolean}
     */
    isEmptyTitle() {
        return this.title.length === 0;
    }

}
