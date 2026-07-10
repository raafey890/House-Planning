function useTheme() {

    const changeTheme = (theme) => {

        console.log(`Theme Changed To ${theme}`);

    };

    return {

        changeTheme

    };
}

export default useTheme;