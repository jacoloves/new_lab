export class EventEmitter {
    #listeners = new Map();

    /**
     * @param {string} type event name
     * @param {FUnction} listener event listener
     */
    addEvenListener(type, listener) {
        if (!this.#listeners.has(type)) {
            this.#listeners.set(type, new Set());
        }
        const listenerSet = this.#listeners.get(type);
        listenerSet.add(listener);
    }

    /**
     * @param {string} type event name
     */
    emit(type) {
        const listenerSet = this.#listeners.get(type);
        if (!listenerSet) {
            return;
        }
        listenerSet.forEach(listener => {
            listener.call(this);
        });
    }

    /**
     * @param {string} type event name
     * @param {FUnction} listener event listener
     */
    removeEventListener(type, listener) {
        const listenerSet = this.#listeners.get(type);
        if (!listenerSet) {
            return;
        }
        listenerSet.forEach(ownListener => {
            if (ownListener === listener) {
                listenerSet.delete(listener);
            }
        });
    }
}
