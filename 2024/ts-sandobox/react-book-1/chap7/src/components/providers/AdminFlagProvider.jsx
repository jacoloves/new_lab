import { createContext, useState } from "react";

export const AdminFlagContext = createContext({});

export const AdminFlagProvider = props => {
    const {children } = props;

    const [isAdmin, setIsAdmin] = useState(false);

    const smapleObj = { sampleValue: "テスト"};

    return (
        <AdminFlagContext.Provider value={{isAdmin, setIsAdmin}}>
            {children}
        </AdminFlagContext.Provider>
    );
};