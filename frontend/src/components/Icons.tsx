import React from "react";
 
interface IconProps {
  size?: number;
  color?: string;
}
 
export const IconHome = ({ size = 28, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8">
    <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z" />
    <path d="M9 21V12h6v9" />
  </svg>
);
 
export const IconMenu = ({ size = 22 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#C0392B" strokeWidth="2">
    <line x1="3" y1="6" x2="21" y2="6" />
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
);
 
export const IconSparkle = ({ size = 14, color = "white" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={color} stroke={color} strokeWidth="1">
    <path d="M12 2l2.4 7.6H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.5 2.4-7.4L2 9.6h7.6z" />
  </svg>
);
 
export const IconArrowRight = ({ size = 20 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M5 12h14M12 5l7 7-7 7" />
  </svg>
);
