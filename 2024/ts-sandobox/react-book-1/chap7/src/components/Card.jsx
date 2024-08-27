import { EditButton } from "./EditButton";

const style = {
    width: "300px",
    height: "200px",
    margin: "8px",
    borderRadius: "8px",
    backgroundColor: "#e9dbdb0",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
};

export const Card = props => {
    return (
        <div style={style}>
            <p>山田太郎</p>
            <EditButton />
        </div>
    );
};