export const ColoredMessage = (props) => {
    console.log("レンダリング");
    
    const { color, children } = props;

    const contentStyle = {
        color: color,
        fontSize: "20px"
    };

    return <p style={contentStyle}>{children}</p>;
}