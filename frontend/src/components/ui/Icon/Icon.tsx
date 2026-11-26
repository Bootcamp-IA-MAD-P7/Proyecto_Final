import type { ReactNode, SVGProps } from "react";

type IconName = "audio" | "check" | "document" | "home" | "upload" | "user";

interface IconProps extends SVGProps<SVGSVGElement> { name: IconName; }

const paths: Record<IconName, ReactNode> = {
  audio: <><path d="M12 4v16" /><path d="M8 8v8" /><path d="M16 7v10" /><path d="M4 10v4" /><path d="M20 10v4" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  document: <><path d="M7 3h7l3 3v15H7z" /><path d="M14 3v4h4" /><path d="M10 12h5M10 16h5" /></>,
  home: <><path d="m3 11 9-8 9 8" /><path d="M5 10v10h14V10" /><path d="M10 20v-6h4v6" /></>,
  upload: <><path d="M12 16V4" /><path d="m8 8 4-4 4 4" /><path d="M5 14v6h14v-6" /></>,
  user: <><circle cx="12" cy="8" r="3" /><path d="M5 21c.7-4 3.1-6 7-6s6.3 2 7 6" /></>
};

export function Icon({ name, ...props }: IconProps) {
  return <svg aria-hidden="true" fill="none" height="1em" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="1em" {...props}>{paths[name]}</svg>;
}
