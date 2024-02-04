import { FC, useState } from 'react'
import { NewTodoPayload } from '../types/todo'
import { Box, TextField, Button, Paper, Grid } from '@mui/material'

// point 1
type Prosp = {
    onSubmit: (newTodo: NewTodoPayload) => void
}

const TodoForm: FC<Prosp> = ({ onSubmit }) => {
    // point 2
    const [editText, setEditText] = useState('')

    // point 3
    const addTodoHandler = async () => {
        if (!editText) return

        onSubmit({
            text: editText,
        })
        setEditText('')
    }

    // point 4
    return (
        <Paper elevation={2}>
            <Box sx={{ p: 2 }}>
                <Grid container rowSpacing={2} columnSpacing={5}>
                    <Grid item xs={12}>
                        <TextField
                            label="new todo text"
                            variant="filled"
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            fullWidth
                        />
                        <Grid item xs={9} />
                        <Grid item xs={3}>
                            <Button onClick={addTodoHandler} fullWidth>
                                add todo
                            </Button>
                        </Grid>
                    </Grid>
                </Grid>
            </Box>
        </Paper>
    )
}

export default TodoForm