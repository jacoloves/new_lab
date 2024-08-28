import { useState } from "react";
import { useFetchUsers } from "./hooks/userFetchUsers";

export const App = () => {
  const { userList, isLoading, isError, onClickFetchUser } = useFetchUsers();

  return (
    <div>
      <button onClick={onClickFetchUser}>ユーザー取得</button>
      {isError && <p style={{ color: "red" }}>エラーが発生しました</p>}

      {isLoading ? (
        <p>データしゅとくちゅうです</p>
      ) : (
        userList.map(user => (
          <p key={user.id}>{`${user.id}:${user.name}(${user.age}歳)`}</p>
        ))
      )}
    </div>
  );
};