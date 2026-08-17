"use client";

import { createTheme, ThemeProvider } from "@mui/material/styles";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { colors } from "@/theme/tokens";

export const muiTheme = createTheme({
    palette: {
        primary: {
            main: colors.primary[600],
        },
    },
    shape: {
        borderRadius: 8,
    },
    typography: {
        fontFamily: "var(--font-inter), ui-sans-serif, system-ui, sans-serif",
    },
});

export function MuiDatePickerProvider({ children }: { children: React.ReactNode}) {
    return (
        <ThemeProvider theme={muiTheme}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                {children}
            </LocalizationProvider>
        </ThemeProvider>
    );
}