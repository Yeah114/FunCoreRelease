import nbtlib
import struct
from io import BytesIO

endian: str = '<'
endianWord: str = 'little'

def getValueType(value) -> bytes:
    """获取NBT值的类型标识"""
    match type(value):
        case nbtlib.tag.Byte:
            return b'\x01'
        case nbtlib.tag.Short:
            return b'\x02'
        case nbtlib.tag.Int:
            return b'\x03'
        case nbtlib.tag.Long:
            return b'\x04'
        case nbtlib.tag.Float:
            return b'\x05'
        case nbtlib.tag.Double:
            return b'\x06'
        case nbtlib.tag.ByteArray:
            return b'\x07'
        case nbtlib.tag.String:
            return b'\x08'
        case nbtlib.tag.Compound:
            return b'\x0a'
        case nbtlib.tag.IntArray:
            return b'\x0b'
        case nbtlib.tag.LongArray:
            return b'\x0c'
        case _:
            return b'\x09'

def marshalToName(writer: BytesIO, name: str) -> None:
    """将名称写入NBT流"""
    encodeResult = name.encode(encoding='utf-8')
    writer.write(struct.pack(f'{endian}H', len(encodeResult)) + encodeResult)

def marshalToValue(writer: BytesIO, value, valueType: int) -> None:
    """将值写入NBT流"""
    match valueType:
        case 1:
            writer.write(value.to_bytes(length = 1, byteorder = endianWord, signed = True))
        case 2:
            writer.write(struct.pack(f'{endian}h', value))
        case 3:
            writer.write(struct.pack(f'{endian}i', value))
        case 4:
            writer.write(struct.pack(f'{endian}q', value))
        case 5:
            writer.write(struct.pack(f'{endian}f', value))
        case 6:
            writer.write(struct.pack(f'{endian}d', value))
        case 7 | 11 | 12:
            marshalToArray(writer, value, valueType)
        case 8:
            marshalToName(writer, str(value))
        case 9:
            marshalToList(writer, value)
        case 10:
            marshalToCompound(writer, value)

def marshalToArray(
    writer: BytesIO,
    value: nbtlib.tag.ByteArray | nbtlib.tag.IntArray | nbtlib.tag.LongArray,
    valueType: int
) -> None:
    """将数组类型写入NBT流"""
    writer.write(struct.pack(f'{endian}i', len(value)))
    match valueType:
        case 7:
            writer.write(b''.join([struct.pack(f'{endian}b', i) for i in value]))
        case 11:
            writer.write(b''.join([struct.pack(f'{endian}i', i) for i in value]))
        case 12:
            writer.write(b''.join([struct.pack(f'{endian}q', i) for i in value]))
        case _:
            raise TypeError("Unsupported array type")

def marshalToList(writer: BytesIO, value) -> None:
    """将列表类型写入NBT流"""
    if len(value) > 0:
        subValueType = getValueType(value[0])
        writer.write(subValueType + struct.pack(f'{endian}i', len(value)))
        for i in value:
            marshalToValue(writer, i, subValueType[0])
    else:
        writer.write(b'\x00' * 5)

def marshalToCompound(writer: BytesIO, value: nbtlib.tag.Compound) -> None:
    """将复合类型写入NBT流"""
    for i in value:
        valueType = getValueType(value[i])
        writer.write(valueType)
        marshalToName(writer, i)
        marshalToValue(writer, value[i], valueType[0])
    writer.write(b'\x00')

def MarshalPythonNBTObjectToWriter(writer: BytesIO, value, name: str) -> None:
    """将Python NBT对象序列化到写入器"""
    valueType = getValueType(value)
    writer.write(valueType)
    marshalToName(writer, name)
    marshalToValue(writer, value, valueType[0])