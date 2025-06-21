import React from "react";
import { Stage, Layer, Rect, Text, Group } from "react-konva";

const CanvasArea = ({ widgets }) => {
  const startX = 50;
  const startY = 100;
  const spacing = 120;

  return (
    <Stage width={window.innerWidth} height={window.innerHeight} style={{ background: "#0e0e0e" }}>
      <Layer>
        <Text text="🧠 MindCanvas" x={20} y={20} fontSize={30} fill="#00FFD1" />

        {widgets.map((widget, i) => {
          const posY = startY + i * spacing;

          if (widget.widget === "habit_tracker") {
            return (
              <Group key={`habit-${i}`}>
                <Text text="Habit Tracker" x={startX} y={posY - 30} fontSize={20} fill="#FFD700" />
                {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, j) => (
                  <Rect
                    key={j}
                    x={startX + j * 80}
                    y={posY}
                    width={70}
                    height={50}
                    fill="#333"
                    stroke="#888"
                    cornerRadius={8}
                    shadowBlur={5}
                  />
                ))}
              </Group>
            );
          }

          if (widget.widget === "mood_tracker") {
            return (
              <Group key={`mood-${i}`}>
                <Text text="Mood Tracker" x={startX} y={posY - 30} fontSize={20} fill="#1FC2A1" />
                {["😀", "😐", "😢"].map((mood, j) => (
                  <Text key={j} text={mood} x={startX + j * 100} y={posY} fontSize={40} fill="#FFF" />
                ))}
              </Group>
            );
          }

          if (widget.widget === "note_taker") {
            return (
              <Group key={`note-${i}`}>
                <Text text="Notes 📝" x={startX} y={posY - 30} fontSize={20} fill="#FFD1DC" />
                <Rect
                  x={startX}
                  y={posY}
                  width={600}
                  height={100}
                  fill="#222"
                  stroke="#fff"
                  cornerRadius={10}
                  shadowBlur={10}
                />
                <Text
                  text={widget.content || "Add your thoughts..."}
                  x={startX + 10}
                  y={posY + 10}
                  fontSize={16}
                  fill="#fff"
                  width={580}
                />
              </Group>
            );
          }

          if (widget.widget === "unsupported") {
            return (
              <Group key={`unknown-${i}`}>
                <Text
                  text={`🤖 Sorry, "${widget.query}" isn't supported yet.`}
                  x={startX}
                  y={posY}
                  fontSize={18}
                  fill="#ff9f43"
                />
              </Group>
            );
          }

          return (
            <Group key={`unsupported-${i}`}>
              <Text
                text={`❌ "${widget.widget}" is not supported yet.`}
                x={startX}
                y={posY}
                fontSize={18}
                fill="#ff4d4d"
              />
            </Group>
          );
        })}
      </Layer>
    </Stage>
  );
};

export default CanvasArea;
